#!/usr/bin/env node
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { createRequire } from 'node:module'

const appRequire = createRequire(path.join(process.cwd(), 'package.json'))
const dotenv = appRequire('dotenv')
const { initializeApp, getApps, cert } = appRequire('firebase-admin/app')
const { getFirestore } = appRequire('firebase-admin/firestore')

const args = process.argv.slice(2)
function arg(name, fallback = '') {
  const index = args.indexOf(`--${name}`)
  return index >= 0 ? args[index + 1] ?? fallback : fallback
}

const orgId = arg('org', 'pib-platform-owner')
const conversationId = arg('conversation', 'CS0TqDu1FJGUK65jdq96')
const writeHtml = args.includes('--html')

dotenv.config({ path: '.env.local', quiet: true })

if (!getApps().length) {
  initializeApp({
    credential: cert({
      projectId: process.env.FIREBASE_ADMIN_PROJECT_ID?.trim(),
      clientEmail: process.env.FIREBASE_ADMIN_CLIENT_EMAIL?.trim(),
      privateKey: process.env.FIREBASE_ADMIN_PRIVATE_KEY?.replace(/\\n/g, '\n').trim(),
    }),
  })
}

const db = getFirestore()
const ts = (value) => value?.toDate ? value.toDate().toISOString() : value ?? null
const policy = JSON.parse(await fs.readFile(path.join(process.cwd(), 'config/agent-skill-policy.json'), 'utf8'))

const focusSkills = [
  'approval-queue-gather',
  'chat-surface-gather',
  'ceo-on-demand-gather',
  'crm-hygiene-gather',
  'social-recovery-gather',
  'agent-runtime-gather',
  'agent-skill-drift-gather',
]

function normalizeSkillName(value) {
  if (typeof value === 'string') return value.trim() || null
  if (!value || typeof value !== 'object') return null
  for (const key of ['name', 'id', 'path', 'skill', 'slug']) {
    const raw = value[key]
    if (typeof raw === 'string' && raw.trim()) return raw.trim()
  }
  return null
}

function uniqueSorted(values) {
  return Array.from(new Set(values.filter(Boolean))).sort()
}

function normalizeInstalledSkillNames(value) {
  const rawList = Array.isArray(value)
    ? value
    : value && typeof value === 'object' && Array.isArray(value.skills)
      ? value.skills
      : []
  return uniqueSorted(rawList.map(normalizeSkillName))
}

function skillBasename(skill) {
  const parts = String(skill).split('/').filter(Boolean)
  return parts.at(-1) ?? skill
}

function classifyInstalledSkills(installed) {
  const catalogPaths = new Set(Object.keys(policy.skillCatalog))
  const catalogByBase = new Map(Object.keys(policy.skillCatalog).map((skill) => [skillBasename(skill), skill]))
  const policyGlobals = new Set(Object.values(policy.agents).flatMap((agentPolicy) => agentPolicy.globalSkills ?? []))
  const pib = []
  const global = []

  for (const skill of installed) {
    const normalized = String(skill ?? '').trim()
    if (!normalized) continue

    if (policyGlobals.has(normalized)) {
      global.push(normalized)
      continue
    }

    if (normalized.startsWith('partnersinbiz/')) {
      const repoSkill = normalized.slice('partnersinbiz/'.length)
      if (catalogPaths.has(repoSkill)) pib.push(repoSkill)
      else global.push(normalized)
      continue
    }

    if (catalogPaths.has(normalized)) {
      pib.push(normalized)
      continue
    }

    if (normalized.includes('/')) {
      global.push(normalized)
      continue
    }

    const catalogSkill = catalogByBase.get(skillBasename(normalized))
    if (catalogSkill) pib.push(catalogSkill)
    else global.push(normalized)
  }

  return { pib: uniqueSorted(pib), global: uniqueSorted(global) }
}

function diff(expected, installed) {
  const installedSet = new Set(installed ?? [])
  const expectedSet = new Set(expected ?? [])
  return {
    missing: (expected ?? []).filter((skill) => !installedSet.has(skill)).sort(),
    unexpected: (installed ?? []).filter((skill) => !expectedSet.has(skill)).sort(),
  }
}

function policyRow(agentId, data) {
  const expected = policy.agents[agentId]
  const storedPolicy = data.skillPolicy ?? null
  const advertised = classifyInstalledSkills(normalizeInstalledSkillNames(data.skills ?? data.installedSkills ?? []))
  const expectedRuntime = expected?.runtimeSkills?.length ? expected.runtimeSkills : expected?.pibSkills ?? []
  const expectedGlobal = expected?.globalSkills ?? []
  const storedRuntime = Array.isArray(storedPolicy?.runtimeSkills) ? storedPolicy.runtimeSkills : []
  const storedGlobal = Array.isArray(storedPolicy?.globalSkills) ? storedPolicy.globalSkills : []
  const storedRuntimeDiff = diff(expectedRuntime, storedRuntime)
  const storedGlobalDiff = diff(expectedGlobal, storedGlobal)
  const advertisedPibDiff = diff(expectedRuntime, advertised.pib)
  const advertisedGlobalDiff = diff(expectedGlobal, advertised.global)
  const missingFocusSkills = focusSkills.filter((skill) => expectedRuntime.includes(skill) && !storedRuntime.includes(skill))
  const advertisedMissingFocusSkills = focusSkills.filter((skill) => expectedRuntime.includes(skill) && !advertised.pib.includes(skill))
  const policyVersionCurrent = storedPolicy?.policyVersion === policy.version
  const catalogVersionCurrent = storedPolicy?.catalogVersion === policy.catalogVersion
  const storedInSync = policyVersionCurrent
    && catalogVersionCurrent
    && storedRuntimeDiff.missing.length === 0
    && storedRuntimeDiff.unexpected.length === 0
    && storedGlobalDiff.missing.length === 0
    && storedGlobalDiff.unexpected.length === 0

  return {
    agentId,
    name: data.name || data.displayName || agentId,
    role: data.role || data.kind || null,
    enabled: data.enabled === true,
    hasBaseUrl: Boolean(data.baseUrl),
    updatedAt: ts(data.updatedAt),
    expectedRuntimeSkills: expectedRuntime.length,
    advertisedPibSkills: advertised.pib.length,
    storedPolicy: {
      exists: Boolean(storedPolicy),
      policyVersion: storedPolicy?.policyVersion ?? null,
      catalogVersion: storedPolicy?.catalogVersion ?? null,
      appliedVersion: storedPolicy?.appliedVersion ?? null,
      driftStatus: storedPolicy?.driftStatus ?? null,
      vpsExternalDir: storedPolicy?.vpsExternalDir ?? null,
      runtimeSkills: storedRuntime.length,
      globalSkills: storedGlobal.length,
    },
    status: storedInSync ? 'in_sync' : 'drifted',
    policyVersionCurrent,
    catalogVersionCurrent,
    storedRuntimeMissing: storedRuntimeDiff.missing,
    storedRuntimeUnexpected: storedRuntimeDiff.unexpected,
    storedGlobalMissing: storedGlobalDiff.missing,
    storedGlobalUnexpected: storedGlobalDiff.unexpected,
    advertisedPibMissing: advertisedPibDiff.missing,
    advertisedPibUnexpected: advertisedPibDiff.unexpected,
    advertisedGlobalMissing: advertisedGlobalDiff.missing,
    advertisedGlobalUnexpected: advertisedGlobalDiff.unexpected,
    missingFocusSkills,
    advertisedMissingFocusSkills,
  }
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

async function main() {
  const [agentsSnap, convSnap] = await Promise.all([
    db.collection('agent_team').get(),
    db.collection('conversations').doc(conversationId).get(),
  ])

  const rows = agentsSnap.docs
    .filter((doc) => policy.agents[doc.id])
    .map((doc) => policyRow(doc.id, doc.data()))
    .sort((a, b) => a.agentId.localeCompare(b.agentId))

  const drifted = rows.filter((row) => row.status !== 'in_sync')
  const missingFocusBySkill = Object.fromEntries(focusSkills.map((skill) => [
    skill,
    rows.filter((row) => row.missingFocusSkills.includes(skill)).map((row) => row.agentId),
  ]))

  const result = {
    checkedAt: new Date().toISOString(),
    orgId,
    conversation: convSnap.exists
      ? {
          id: conversationId,
          messageCount: convSnap.get('messageCount') ?? null,
          lastMessageId: convSnap.get('lastMessageId') ?? null,
        }
      : { id: conversationId, exists: false },
    manifest: {
      version: policy.version,
      catalogVersion: policy.catalogVersion,
      agents: Object.keys(policy.agents).length,
      repoPibSkills: policy.repoPibSkills.length,
      focusSkills,
    },
    summary: {
      agentsChecked: rows.length,
      enabled: rows.filter((row) => row.enabled).length,
      missingBaseUrl: rows.filter((row) => !row.hasBaseUrl).map((row) => row.agentId),
      inSync: rows.length - drifted.length,
      drifted: drifted.length,
      missingFocusBySkill,
    },
    rows,
    safety: 'Read-only agent skill drift gather. No agent_team, Hermes/VPS config, task, release, env, secret, or destructive mutation performed.',
  }

  if (writeHtml) {
    const file = path.join(os.tmpdir(), `pib-agent-skill-drift-${orgId}-${Date.now()}.html`)
    const html = `<!doctype html><meta charset="utf-8"><title>PiB Agent Skill Drift</title><style>body{font-family:system-ui,sans-serif;margin:32px;color:#111}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;vertical-align:top;text-align:left}th{background:#f4f4f4}.bad{color:#a40000;font-weight:700}.ok{color:#146b2e;font-weight:700}code{font-size:12px}</style><h1>PiB Agent Skill Drift</h1><p>${escapeHtml(result.checkedAt)} | manifest ${escapeHtml(policy.version)} / ${escapeHtml(policy.catalogVersion)}</p><table><thead><tr><th>Agent</th><th>Status</th><th>Stored policy</th><th>Missing focus skills</th><th>Runtime missing count</th></tr></thead><tbody>${rows.map((row) => `<tr><td><code>${escapeHtml(row.agentId)}</code><br>${escapeHtml(row.name)}</td><td class="${row.status === 'in_sync' ? 'ok' : 'bad'}">${escapeHtml(row.status)}</td><td>${escapeHtml(row.storedPolicy.policyVersion)}<br>${escapeHtml(row.storedPolicy.catalogVersion)}</td><td>${escapeHtml(row.missingFocusSkills.join(', ') || 'none')}</td><td>${escapeHtml(row.storedRuntimeMissing.length)}</td></tr>`).join('')}</tbody></table>`
    await fs.writeFile(file, html)
    result.tempHtml = file
  }

  console.log(JSON.stringify(result, null, 2))
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
