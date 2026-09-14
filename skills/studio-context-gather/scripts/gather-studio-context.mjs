#!/usr/bin/env node
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const MAX_RESPONSE_BYTES = 256 * 1024
const DEFAULT_TIMEOUT_MS = 10_000
const productionHosts = new Set(['partnersinbiz.online', 'www.partnersinbiz.online'])
const loopbackHosts = new Set(['localhost', '127.0.0.1', '[::1]'])

export const definitions = {
  marketing: { workspace: '/portal/marketing', resources: { canvases: (value) => `/api/v1/creative-canvas/${encodeURIComponent(value)}` } },
  video: { workspace: '/portal/video-editor', resources: { projects: (value) => `/api/v1/video-editor/projects/${encodeURIComponent(value)}` } },
  book: { workspace: '/portal/book-studio', resources: { projects: (value) => `/api/v1/book-studio/projects?id=${encodeURIComponent(value)}` } },
  youtube: { workspace: '/portal/youtube-studio', resources: { videos: (value) => `/api/v1/youtube-studio/videos/${encodeURIComponent(value)}` } },
  mobile_apps: { workspace: '/portal/mobile-apps', resources: { apps: (value) => `/api/v1/mobile-apps/${encodeURIComponent(value)}` } },
}

export const checkedFields = [
  'id', 'title|name|label', 'lifecycleStatus|status|state',
  'versionId|currentVersionId|revision', 'blockers|blockedReason|attention',
  'approval|approvalStatus|approvalGate', 'updatedAt|modifiedAt', 'lineage',
]

function cleanString(value, max = 500) {
  return typeof value === 'string' ? value.trim().slice(0, max) || null : null
}

function cleanScalar(value) {
  if (typeof value === 'boolean' || typeof value === 'number') return value
  return cleanString(value)
}

function projectNamedFields(value, fields) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return cleanScalar(value)
  return Object.fromEntries(fields.flatMap((field) => {
    const projected = cleanScalar(value[field])
    return projected === null || projected === undefined ? [] : [[field, projected]]
  }))
}

function projectBlockers(value) {
  const values = Array.isArray(value) ? value : value === null || value === undefined ? [] : [value]
  return values.slice(0, 20).map((item) => projectNamedFields(item, ['code', 'message', 'status', 'severity'])).filter((item) => item !== null)
}

function projectApproval(value) {
  return projectNamedFields(value, ['status', 'requiredBy', 'reviewer', 'decision', 'decidedAt'])
}

export function projectSafeRecord(source, { expectedId, conversationId = null, originMessageId = null } = {}) {
  if (!source || typeof source !== 'object' || Array.isArray(source)) throw new Error('Studio context unavailable (invalid record)')
  if (source.id !== expectedId) throw new Error('Studio context unavailable (record ID mismatch)')
  const lineage = source.lineage && typeof source.lineage === 'object' && !Array.isArray(source.lineage) ? source.lineage : {}
  return {
    id: cleanString(source.id, 200),
    title: cleanString(source.title ?? source.name ?? source.label),
    status: cleanString(source.lifecycleStatus ?? source.status ?? source.state, 100),
    versionId: cleanString(source.versionId ?? source.currentVersionId ?? source.revision, 200),
    blockers: projectBlockers(source.blockers ?? source.blockedReason ?? source.attention),
    approval: projectApproval(source.approval ?? source.approvalStatus ?? source.approvalGate),
    updatedAt: cleanString(source.updatedAt ?? source.modifiedAt, 100),
    lineage: {
      conversationId: cleanString(lineage.conversationId ?? source.conversationId ?? conversationId, 200),
      originMessageId: cleanString(lineage.originMessageId ?? source.originMessageId ?? originMessageId, 200),
      sourceArtifactId: cleanString(lineage.sourceArtifactId ?? source.sourceArtifactId, 200),
      sourceVersionId: cleanString(lineage.sourceVersionId ?? source.sourceVersionId, 200),
    },
  }
}

export function parsePreviewOrigins(value = '') {
  const origins = new Set()
  for (const entry of value.split(',').map((item) => item.trim()).filter(Boolean)) {
    let url
    try { url = new URL(entry) } catch { throw new Error('Preview allowlist origin is invalid') }
    if (url.protocol !== 'https:' || url.username || url.password || url.pathname !== '/' || url.search || url.hash || url.port) {
      throw new Error('Preview allowlist origin is invalid')
    }
    origins.add(url.origin)
  }
  return origins
}

export function validateApiBaseUrl(value, { allowLocalhost = false, allowedPreviewOrigins = new Set() } = {}) {
  let url
  try { url = new URL(value) } catch { throw new Error('PIB_API_BASE_URL is not allowed') }
  const isLoopback = loopbackHosts.has(url.hostname)
  const isAllowedRemote = url.protocol === 'https:' && (productionHosts.has(url.hostname) || allowedPreviewOrigins.has(url.origin))
  const isAllowedLoopback = allowLocalhost && isLoopback && (url.protocol === 'http:' || url.protocol === 'https:')
  if ((!isAllowedRemote && !isAllowedLoopback) || (!isLoopback && url.port) || url.username || url.password || url.pathname !== '/' || url.search || url.hash) {
    throw new Error('PIB_API_BASE_URL is not allowed')
  }
  return url
}

async function readBoundedJson(response, maxBytes) {
  const contentType = response.headers.get('content-type')?.toLowerCase() ?? ''
  if (!contentType.includes('application/json')) throw new Error('Studio context unavailable (invalid response)')
  const declaredLength = Number(response.headers.get('content-length'))
  if (Number.isFinite(declaredLength) && declaredLength > maxBytes) throw new Error('Studio context unavailable (response too large)')
  if (!response.body) throw new Error('Studio context unavailable (invalid response)')
  const reader = response.body.getReader()
  const chunks = []
  let length = 0
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    length += value.byteLength
    if (length > maxBytes) {
      await reader.cancel()
      throw new Error('Studio context unavailable (response too large)')
    }
    chunks.push(value)
  }
  const bytes = new Uint8Array(length)
  let offset = 0
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength }
  try { return JSON.parse(new TextDecoder().decode(bytes)) } catch { throw new Error('Studio context unavailable (invalid response)') }
}

function correlationKey({ orgId, studio, resource, id, conversationId, originMessageId }) {
  const identity = [orgId, studio, resource, id, conversationId ?? '', originMessageId ?? ''].join('\u001f')
  return `studio-context-read:${createHash('sha256').update(identity).digest('hex')}`
}

export async function gatherStudioContext(input) {
  const { studio, resource, id, orgId, conversationId = null, originMessageId = null, apiKey } = input
  for (const [value, label] of [[studio, 'studio'], [resource, 'resource'], [id, 'id'], [orgId, 'org']]) {
    if (typeof value !== 'string' || !value.trim()) throw new Error(`Missing --${label}`)
  }
  if (typeof apiKey !== 'string' || !apiKey.trim()) throw new Error('AI_API_KEY is not configured in .env.local')
  const definition = definitions[studio]
  const endpoint = definition?.resources?.[resource]?.(id)
  if (!endpoint) throw new Error(`Unsupported read-only Studio resource: ${studio}/${resource}`)
  const baseUrl = validateApiBaseUrl(input.baseUrl ?? 'https://partnersinbiz.online', {
    allowLocalhost: input.allowLocalhost === true,
    allowedPreviewOrigins: input.allowedPreviewOrigins ?? new Set(),
  })
  const requestUrl = new URL(endpoint, baseUrl)
  const controller = new AbortController()
  const timeoutMs = Number.isFinite(input.timeoutMs) ? Math.max(1, input.timeoutMs) : DEFAULT_TIMEOUT_MS
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  let body
  try {
    const response = await (input.fetchImpl ?? fetch)(requestUrl.href, {
      method: 'GET',
      headers: { Authorization: `Bearer ${apiKey.trim()}`, 'X-Org-Id': orgId.trim() },
      redirect: 'error',
      signal: controller.signal,
    })
    if (!response.ok) throw new Error(`Studio context unavailable (${response.status})`)
    body = await readBoundedJson(response, input.maxResponseBytes ?? MAX_RESPONSE_BYTES)
  } catch (error) {
    if (controller.signal.aborted) throw new Error('Studio context request timed out')
    if (error instanceof Error && error.message.startsWith('Studio context unavailable')) throw error
    throw new Error('Studio context unavailable (request failed)')
  } finally {
    clearTimeout(timer)
  }
  const data = body?.data ?? body
  const candidate = Array.isArray(data) ? data.find((item) => item?.id === id)
    : Array.isArray(data?.items) ? data.items.find((item) => item?.id === id) : data
  if (!candidate) throw new Error('Studio context unavailable (record not found)')
  const record = projectSafeRecord(candidate, { expectedId: id, conversationId, originMessageId })
  const missingFields = Object.entries(record.lineage).filter(([, value]) => !value).map(([field]) => field)
  const canonicalLink = new URL(`${definition.workspace}?resource=${encodeURIComponent(resource)}&id=${encodeURIComponent(id)}`, baseUrl).href
  return {
    checkedAt: new Date().toISOString(),
    correlationKey: correlationKey({ orgId, studio, resource, id, conversationId, originMessageId }),
    studioKind: studio,
    resourceType: resource,
    orgId,
    checkedEndpoint: { method: 'GET', path: endpoint },
    checkedFields,
    canonicalLink,
    record: { ...record, canonicalLink },
    blocker: missingFields.length ? { code: 'missing_lineage', message: 'Studio context is read-only until required lineage is resolved.', missingFields } : null,
    safety: 'Read-only existing API request. No generation, review, approval, export, publish, provider, connection, or secret mutation performed.',
  }
}

function arg(args, name) {
  const index = args.indexOf(`--${name}`)
  return index >= 0 ? args[index + 1]?.trim() : undefined
}

async function main() {
  const appRequire = createRequire(path.join(process.cwd(), 'package.json'))
  appRequire('dotenv').config({ path: '.env.local', quiet: true })
  const args = process.argv.slice(2)
  const result = await gatherStudioContext({
    studio: arg(args, 'studio'), resource: arg(args, 'resource'), id: arg(args, 'id'), orgId: arg(args, 'org'),
    conversationId: arg(args, 'conversation') ?? null, originMessageId: arg(args, 'origin-message') ?? null,
    baseUrl: process.env.PIB_API_BASE_URL || 'https://partnersinbiz.online', apiKey: process.env.AI_API_KEY,
    allowedPreviewOrigins: parsePreviewOrigins(process.env.PIB_API_PREVIEW_ORIGINS),
    allowLocalhost: process.env.NODE_ENV === 'development' && process.env.PIB_ALLOW_LOCALHOST === 'true',
  })
  console.log(JSON.stringify(result, null, 2))
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : 'Studio context unavailable')
    process.exitCode = 1
  })
}
