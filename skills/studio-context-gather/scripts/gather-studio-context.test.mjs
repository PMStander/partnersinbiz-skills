import assert from 'node:assert/strict'
import test from 'node:test'

import {
  gatherStudioContext,
  parsePreviewOrigins,
  projectSafeRecord,
  validateApiBaseUrl,
} from './gather-studio-context.mjs'

const completeLineage = {
  conversationId: 'conversation-1',
  originMessageId: 'message-1',
  sourceArtifactId: 'artifact-1',
  sourceVersionId: 'version-1',
}

function response(body, init = {}) {
  return new Response(typeof body === 'string' ? body : JSON.stringify(body), {
    status: 200,
    headers: { 'content-type': 'application/json' },
    ...init,
  })
}

test('accepts production and only exact operator-allowlisted Preview HTTPS origins', () => {
  assert.equal(validateApiBaseUrl('https://partnersinbiz.online').origin, 'https://partnersinbiz.online')
  assert.throws(() => validateApiBaseUrl('https://partnersinbiz-web-git-development-peetstander.vercel.app/'), /not allowed/)
  const allowedPreviewOrigins = parsePreviewOrigins('https://partnersinbiz-web-git-development-peetstander.vercel.app')
  assert.equal(validateApiBaseUrl('https://partnersinbiz-web-git-development-peetstander.vercel.app/', { allowedPreviewOrigins }).protocol, 'https:')
  for (const value of [
    'http://partnersinbiz.online',
    'https://partnersinbiz.online:8443',
    'https://partnersinbiz.online.evil.test',
    'https://evil.test',
    'file:///etc/passwd',
    'https://user:pass@partnersinbiz.online',
  ]) assert.throws(() => validateApiBaseUrl(value), /not allowed/)
  for (const configured of ['http://preview.vercel.app', 'https://preview.vercel.app/path', 'https://user:pass@preview.vercel.app']) {
    assert.throws(() => parsePreviewOrigins(configured), /Preview allowlist origin is invalid/)
  }
})

test('allows loopback only behind explicit development opt-in', () => {
  assert.throws(() => validateApiBaseUrl('http://127.0.0.1:3210'), /not allowed/)
  assert.equal(validateApiBaseUrl('http://localhost:3210', { allowLocalhost: true }).port, '3210')
  assert.equal(validateApiBaseUrl('http://[::1]:3210', { allowLocalhost: true }).hostname, '[::1]')
})

test('encodes path and query arguments and refuses redirects while scoping auth', async () => {
  let request
  await gatherStudioContext({
    studio: 'book', resource: 'projects', id: 'a/b?x=1', orgId: 'org value', apiKey: 'secret',
    fetchImpl: async (url, init) => {
      request = { url, init }
      return response({ data: { id: 'a/b?x=1', lineage: completeLineage } })
    },
  })
  assert.equal(request.url, 'https://partnersinbiz.online/api/v1/book-studio/projects?id=a%2Fb%3Fx%3D1')
  assert.equal(request.init.redirect, 'error')
  assert.equal(request.init.headers.Authorization, 'Bearer secret')
  assert.equal(request.init.headers['X-Org-Id'], 'org value')
  assert.ok(request.init.signal instanceof AbortSignal)
})

test('projects only bounded status, blocker, approval, and lineage fields', () => {
  const projected = projectSafeRecord({
    id: 'item-1', title: 'Title', state: 'draft', revision: 'v1',
    blockers: Array.from({ length: 30 }, (_, index) => ({ code: `b${index}`, message: 'x'.repeat(1000), secret: 'no' })),
    approval: { status: 'pending', requiredBy: 'CEO', token: 'no', nested: { password: 'no' } },
    lineage: { ...completeLineage, apiKey: 'no' }, apiKey: 'no', password: 'no', unexpected: 'no',
  }, { expectedId: 'item-1' })
  assert.deepEqual(Object.keys(projected), ['id', 'title', 'status', 'versionId', 'blockers', 'approval', 'updatedAt', 'lineage'])
  assert.equal(projected.blockers.length, 20)
  assert.deepEqual(projected.approval, { status: 'pending', requiredBy: 'CEO' })
  assert.deepEqual(projected.lineage, completeLineage)
  assert.doesNotMatch(JSON.stringify(projected), /secret|password|apiKey|unexpected/)
})

test('rejects non-JSON, HTTP failures, oversized responses, and exact ID mismatch with safe errors', async () => {
  const cases = [
    [async () => response('<html>oops</html>', { headers: { 'content-type': 'text/html' } }), /invalid response/],
    [async () => response({ error: 'Bearer secret database password' }, { status: 403 }), /unavailable \(403\)/],
    [async () => response({ data: { id: 'item-1' } }, { headers: { 'content-type': 'application/json', 'content-length': '9999999' } }), /response too large/],
    [async () => response({ data: { id: 'different' } }), /record ID mismatch/],
  ]
  for (const [fetchImpl, pattern] of cases) {
    await assert.rejects(gatherStudioContext({ studio: 'marketing', resource: 'canvases', id: 'item-1', orgId: 'org-1', apiKey: 'secret', fetchImpl }), pattern)
  }
})

test('times out deterministically without exposing fetch error details', async () => {
  const fetchImpl = async (_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener('abort', () => reject(new Error('secret socket details')), { once: true })
  })
  await assert.rejects(
    gatherStudioContext({ studio: 'marketing', resource: 'canvases', id: 'item-1', orgId: 'org-1', apiKey: 'secret', fetchImpl, timeoutMs: 5 }),
    /^Error: Studio context request timed out$/,
  )
})

test('keeps the timeout active while a response body is streaming', async () => {
  const fetchImpl = async (_url, { signal }) => new Response(new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode('{"data":'))
      signal.addEventListener('abort', () => controller.error(new Error('secret stream detail')), { once: true })
    },
  }), { headers: { 'content-type': 'application/json' } })
  await assert.rejects(
    gatherStudioContext({ studio: 'marketing', resource: 'canvases', id: 'item-1', orgId: 'org-1', apiKey: 'secret', fetchImpl, timeoutMs: 5 }),
    /^Error: Studio context request timed out$/,
  )
})

test('reports missing lineage and stable correlation without leaking inputs', async () => {
  const input = { studio: 'marketing', resource: 'canvases', id: 'item-1', orgId: 'org-1', apiKey: 'bearer-value-must-not-leak', fetchImpl: async () => response({ data: { id: 'item-1' } }) }
  const first = await gatherStudioContext(input)
  const second = await gatherStudioContext(input)
  assert.equal(first.correlationKey, second.correlationKey)
  assert.equal(first.blocker.code, 'missing_lineage')
  assert.deepEqual(first.blocker.missingFields, ['conversationId', 'originMessageId', 'sourceArtifactId', 'sourceVersionId'])
  assert.doesNotMatch(JSON.stringify(first), /bearer-value-must-not-leak/)
})
