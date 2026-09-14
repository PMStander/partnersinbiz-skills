#!/usr/bin/env node
import { createRequire } from 'node:module'
import fs from 'node:fs/promises'
import https from 'node:https'
import os from 'node:os'
import path from 'node:path'

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
const baseUrl = arg('base-url', 'https://partnersinbiz.online')
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
const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

function requestHead(url) {
  return new Promise((resolve) => {
    const req = https.request(url, { method: 'HEAD', timeout: 8000 }, (res) => {
      res.resume()
      resolve({
        url,
        status: res.statusCode ?? null,
        location: res.headers.location ?? null,
        contentType: res.headers['content-type'] ?? null,
      })
    })
    req.on('timeout', () => {
      req.destroy(new Error('timeout'))
    })
    req.on('error', (err) => {
      resolve({ url, status: null, error: err.message })
    })
    req.end()
  })
}

function summarizeMessage(doc) {
  const data = doc.data() || {}
  const richParts = Array.isArray(data.richParts) ? data.richParts : Array.isArray(data.rich_parts) ? data.rich_parts : []
  return {
    id: doc.id,
    status: data.status ?? null,
    authorId: data.authorId ?? data.agentId ?? null,
    authorDisplayName: data.authorDisplayName ?? data.authorName ?? null,
    createdAt: ts(data.createdAt),
    updatedAt: ts(data.updatedAt),
    richParts: richParts.length,
    preview: String(data.content ?? data.text ?? '').slice(0, 220),
  }
}

async function main() {
  const convRef = db.collection('conversations').doc(conversationId)
  const [convSnap, latestMessagesSnap, releaseGateSnap] = await Promise.all([
    convRef.get(),
    convRef.collection('messages').orderBy('createdAt', 'desc').limit(12).get(),
    db.collection('tasks').doc('P7wew8tGBP82tb2731xR').get(),
  ])

  const latestMessages = latestMessagesSnap.docs.map(summarizeMessage)
  const latestMessageId = convSnap.exists ? convSnap.get('lastMessageId') ?? null : null
  const latestMessage = latestMessages.find((message) => message.id === latestMessageId) ?? null
  const routeProbes = await Promise.all([
    requestHead(`${baseUrl}/portal/messages`),
    requestHead(`${baseUrl}/portal/conversations?convId=${encodeURIComponent(conversationId)}`),
    requestHead(`${baseUrl}/api/v1/chat-feed/${encodeURIComponent(conversationId)}`),
    requestHead(`${baseUrl}/api/v1/conversations/${encodeURIComponent(conversationId)}/messages`),
  ])

  const releaseOutput = releaseGateSnap.exists ? releaseGateSnap.get('agentOutput') ?? {} : {}
  const result = {
    checkedAt: new Date().toISOString(),
    orgId,
    conversation: convSnap.exists
      ? {
          id: conversationId,
          exists: true,
          messageCount: convSnap.get('messageCount') ?? null,
          lastMessageId: latestMessageId,
          lastMessageAt: ts(convSnap.get('lastMessageAt')),
          latestMessage,
          latestMessages,
        }
      : { id: conversationId, exists: false },
    routes: routeProbes,
    releaseGate: releaseGateSnap.exists
      ? {
          id: releaseGateSnap.id,
          title: releaseGateSnap.get('title') ?? null,
          agentStatus: releaseGateSnap.get('agentStatus') ?? null,
          columnId: releaseGateSnap.get('columnId') ?? null,
          releaseHead: releaseOutput.latestReleaseHeadCorrection?.releaseHead
            ?? releaseOutput.latestChatBodyFallbackFix?.releaseHead
            ?? releaseOutput.latestFocusedConversationRouteFix?.releaseHead
            ?? releaseOutput.latestReleaseSkillPolicyUpdate?.releaseHead
            ?? releaseOutput.releaseHead
            ?? null,
          latestReleaseHeadCorrectionMessageId: releaseOutput.latestReleaseHeadCorrection?.messageId ?? null,
          latestChatBodyFallbackMessageId: releaseOutput.latestChatBodyFallbackFix?.messageId ?? null,
          latestRouteFixMessageId: releaseOutput.latestFocusedConversationRouteFix?.messageId ?? null,
          latestReleasePolicyMessageId: releaseOutput.latestReleaseSkillPolicyUpdate?.messageId ?? null,
        }
      : null,
    assessment: {
      storedConversationReady: convSnap.exists && Boolean(latestMessageId) && Boolean(latestMessage),
      latestMessageHasRichParts: Boolean(latestMessage && latestMessage.richParts > 0),
      focusedRouteFixInRelease: releaseOutput.latestFocusedConversationRouteFix?.releaseHead === 'a7a696f4',
      productionLikelyStillApprovalGated: releaseGateSnap.get('agentStatus') === 'awaiting-input' && releaseGateSnap.get('columnId') === 'blocked',
    },
    safety: 'Read-only chat surface gather. No conversation, task, CRM, social, deploy, env, spend, or destructive mutation performed.',
  }

  if (writeHtml) {
    const html = `<!doctype html><meta charset="utf-8"><title>PiB Chat Surface Gather</title><style>body{font-family:system-ui,sans-serif;margin:32px;color:#111}table{border-collapse:collapse;width:100%;margin:16px 0}td,th{border:1px solid #ddd;padding:8px;vertical-align:top;text-align:left}th{background:#f4f4f4}code{font-size:12px}</style><h1>PiB Chat Surface Gather</h1><p>${escapeHtml(result.checkedAt)} | ${escapeHtml(orgId)}</p><h2>Conversation</h2><table><tbody><tr><th>ID</th><td><code>${escapeHtml(conversationId)}</code></td></tr><tr><th>Message count</th><td>${escapeHtml(result.conversation.messageCount)}</td></tr><tr><th>Latest</th><td><code>${escapeHtml(result.conversation.lastMessageId)}</code></td></tr></tbody></table><h2>Routes</h2><table><thead><tr><th>URL</th><th>Status</th><th>Location/Error</th></tr></thead><tbody>${routeProbes.map((probe) => `<tr><td><code>${escapeHtml(probe.url)}</code></td><td>${escapeHtml(probe.status)}</td><td>${escapeHtml(probe.location ?? probe.error ?? '')}</td></tr>`).join('')}</tbody></table><h2>Latest Messages</h2><table><thead><tr><th>ID</th><th>Status</th><th>Rich parts</th><th>Preview</th></tr></thead><tbody>${latestMessages.map((message) => `<tr><td><code>${escapeHtml(message.id)}</code></td><td>${escapeHtml(message.status)}</td><td>${escapeHtml(message.richParts)}</td><td>${escapeHtml(message.preview)}</td></tr>`).join('')}</tbody></table>`
    const file = path.join(os.tmpdir(), `pib-chat-surface-${orgId}-${Date.now()}.html`)
    await fs.writeFile(file, html)
    result.tempHtml = file
  }

  console.log(JSON.stringify(result, null, 2))
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
