#!/usr/bin/env node
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import process from 'node:process'
import { createRequire } from 'node:module'

const requireFromCwd = createRequire(path.join(process.cwd(), 'package.json'))
const { activeRows } = requireFromCwd('./scripts/crm-gather-active-records')

function arg(name, fallback = null) {
  const index = process.argv.indexOf(`--${name}`)
  if (index === -1) return fallback
  return process.argv[index + 1] && !process.argv[index + 1].startsWith('--')
    ? process.argv[index + 1]
    : true
}

function loadDotenv() {
  try {
    requireFromCwd('dotenv').config({ path: path.join(process.cwd(), '.env.local'), quiet: true })
  } catch {
    // dotenv is available in partnersinbiz-web; fail later if env is missing.
  }
}

function ts(value) {
  if (!value) return null
  if (typeof value.toDate === 'function') return value.toDate().toISOString()
  return value
}

async function main() {
  loadDotenv()
  const { initializeApp, getApps, cert } = requireFromCwd('firebase-admin/app')
  const { getFirestore } = requireFromCwd('firebase-admin/firestore')

  const orgId = String(arg('org', 'pib-platform-owner'))
  const conversationId = String(arg('conversation', 'CS0TqDu1FJGUK65jdq96'))
  const makeHtml = Boolean(arg('html', false))

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
  const count = async (query) => (await query.count().get()).data().count
  const activeCount = async (query) => activeRows((await query.get()).docs.map((doc) => doc.data())).length
  const socialStatuses = ['draft', 'approved', 'scheduled', 'published', 'failed', 'cancelled']
  const socialCounts = {}
  for (const status of socialStatuses) {
    socialCounts[status] = await count(db.collection('social_posts').where('orgId', '==', orgId).where('status', '==', status))
  }

  const [contacts, companies, deals, tasks, conversation, latestMessages, accounts] = await Promise.all([
    activeCount(db.collection('contacts').where('orgId', '==', orgId)).catch((error) => ({ error: error.message })),
    activeCount(db.collection('companies').where('orgId', '==', orgId)).catch((error) => ({ error: error.message })),
    activeCount(db.collection('deals').where('orgId', '==', orgId)).catch((error) => ({ error: error.message })),
    db.collection('tasks').where('orgId', '==', orgId).limit(200).get().catch((error) => ({ error: error.message, docs: [] })),
    db.collection('conversations').doc(conversationId).get(),
    db.collection('conversations').doc(conversationId).collection('messages').orderBy('createdAt', 'desc').limit(10).get(),
    db.collection('social_accounts').where('orgId', '==', orgId).limit(50).get().catch((error) => ({ error: error.message, docs: [] })),
  ])

  const taskRows = tasks.docs.map((doc) => {
    const data = doc.data()
    return {
      id: doc.id,
      title: data.title || null,
      agentStatus: data.agentStatus || null,
      columnId: data.columnId || null,
      assigneeAgentId: data.assigneeAgentId || null,
      updatedAt: ts(data.updatedAt),
    }
  })

  const agentStatusCounts = {}
  for (const task of taskRows) {
    if (!task.assigneeAgentId) continue
    const key = task.agentStatus || 'missing'
    agentStatusCounts[key] = (agentStatusCounts[key] || 0) + 1
  }

  const accountRows = accounts.docs.map((doc) => {
    const data = doc.data()
    return {
      id: doc.id,
      platform: data.platform || null,
      status: data.status || null,
      displayName: data.displayName || data.name || null,
      isDefault: data.isDefault || false,
    }
  })

  const summary = {
    checkedAt: new Date().toISOString(),
    orgId,
    conversation: {
      id: conversationId,
      exists: conversation.exists,
      lastMessageId: conversation.get('lastMessageId') || null,
      messageCount: conversation.get('messageCount') || null,
      latest: latestMessages.docs.map((doc) => ({
        id: doc.id,
        authorId: doc.get('authorId') || null,
        status: doc.get('status') || null,
        richParts: (doc.get('richParts') || []).length,
        createdAt: ts(doc.get('createdAt')),
        preview: String(doc.get('content') || '').slice(0, 160),
      })),
    },
    crm: { contacts, companies, deals },
    social: { counts: socialCounts, accounts: accountRows },
    tasks: { sampled: taskRows.length, agentStatusCounts, rows: taskRows.slice(0, 30) },
    safety: 'Read-only snapshot. No CRM, social, task, approval, billing, env, deploy, or destructive mutation performed.',
  }

  if (makeHtml) {
    const file = path.join(os.tmpdir(), `pib-ceo-snapshot-${orgId}-${Date.now()}.html`)
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>PiB CEO Snapshot</title><style>body{font-family:system-ui,sans-serif;margin:24px;line-height:1.4}table{border-collapse:collapse;width:100%;margin:12px 0}td,th{border:1px solid #ddd;padding:6px;text-align:left}code{background:#f4f4f4;padding:2px 4px}</style></head><body><h1>PiB CEO Snapshot</h1><p><code>${summary.checkedAt}</code></p><h2>CRM</h2><table><tr><th>Contacts</th><th>Companies</th><th>Deals</th></tr><tr><td>${contacts}</td><td>${companies}</td><td>${deals}</td></tr></table><h2>Social Counts</h2><table><tr>${Object.keys(socialCounts).map((k) => `<th>${k}</th>`).join('')}</tr><tr>${Object.values(socialCounts).map((v) => `<td>${v}</td>`).join('')}</tr></table><h2>Agent Task Status</h2><pre>${JSON.stringify(agentStatusCounts, null, 2)}</pre><h2>Latest Messages</h2><pre>${JSON.stringify(summary.conversation.latest, null, 2)}</pre><h2>Safety</h2><p>${summary.safety}</p></body></html>`
    fs.writeFileSync(file, html)
    summary.tempHtml = file
  }

  console.log(JSON.stringify(summary, null, 2))
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
