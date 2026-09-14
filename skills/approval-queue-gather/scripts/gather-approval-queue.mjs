#!/usr/bin/env node
import { createRequire } from 'node:module'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'

const appRequire = createRequire(path.join(process.cwd(), 'package.json'))
const dotenv = appRequire('dotenv')
const { initializeApp, getApps, cert } = appRequire('firebase-admin/app')
const { getFirestore } = appRequire('firebase-admin/firestore')
const { crmCountsFromRows } = appRequire('./scripts/approval-queue-active-crm-counts')

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
const lower = (value) => typeof value === 'string' ? value.trim().toLowerCase() : ''
const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

function classifyTask(task) {
  const title = lower(task.title || task.name || '')
  if (task.id === 'P7wew8tGBP82tb2731xR' || title.includes('release')) return 'release'
  if (task.id === 'FgajS7LxTdYr0f8ywTtf' || title.includes('marketing studio') || title.includes('social')) return 'marketing-studio'
  if (task.id === 'KnY9PLVW6i7r2TfDuzWx' || title.includes('crm') || title.includes('proposal')) return 'crm-sales'
  if (task.id === '0xrbtDWUB50I41WmdZpd' || title.includes('operating queue') || title.includes('approval hygiene')) return 'operations'
  if (title.includes('follow-up')) return 'sales-follow-up'
  return 'other'
}

function recommendationFor(kind) {
  switch (kind) {
    case 'release':
      return 'Review/create the release PR from the compare URL, then approve production only after live verification is planned.'
    case 'marketing-studio':
      return 'Approve exact post IDs and dates before schedule/publish; keep failed-post retry/reconnect separate.'
    case 'crm-sales':
      return 'Approve exact proposal values, close dates, and send copy before CRM mutation or outreach.'
    case 'operations':
      return 'Keep the daily approval queue in Messages and do not auto-clear gates without posted evidence.'
    case 'sales-follow-up':
      return 'Approve, revise, or hold each follow-up before any external message is sent.'
    default:
      return 'Decide whether to approve, revise, hold, or assign a human owner.'
  }
}

async function collectionRows(name) {
  const snap = await db.collection(name).where('orgId', '==', orgId).get()
  return snap.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
}

async function main() {
  const [convSnap, tasksSnap, postsSnap, accountsSnap, contactsRows, companiesRows, dealsRows] = await Promise.all([
    db.collection('conversations').doc(conversationId).get(),
    db.collection('tasks').where('orgId', '==', orgId).get(),
    db.collection('social_posts').where('orgId', '==', orgId).get(),
    db.collection('social_accounts').where('orgId', '==', orgId).get(),
    collectionRows('contacts'),
    collectionRows('companies'),
    collectionRows('deals'),
  ])
  const crmCounts = crmCountsFromRows({
    contacts: contactsRows,
    companies: companiesRows,
    deals: dealsRows,
  })

  const tasks = tasksSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
  const blockedTasks = tasks
    .filter((task) => lower(task.agentStatus) === 'awaiting-input' || lower(task.columnId) === 'blocked')
    .map((task) => {
      const kind = classifyTask(task)
      return {
        id: task.id,
        title: task.title || task.name || '',
        kind,
        assigneeAgentId: task.assigneeAgentId || null,
        agentStatus: task.agentStatus || null,
        columnId: task.columnId || null,
        updatedAt: ts(task.updatedAt),
        recommendation: recommendationFor(kind),
      }
    })
    .sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)))

  const byKind = blockedTasks.reduce((acc, task) => {
    acc[task.kind] = (acc[task.kind] || 0) + 1
    return acc
  }, {})

  const socialCounts = postsSnap.docs.reduce((acc, doc) => {
    const status = doc.get('status') || 'unknown'
    acc[status] = (acc[status] || 0) + 1
    return acc
  }, {})

  const result = {
    checkedAt: new Date().toISOString(),
    orgId,
    conversation: convSnap.exists
      ? {
          id: conversationId,
          messageCount: convSnap.get('messageCount') ?? null,
          lastMessageId: convSnap.get('lastMessageId') ?? null,
        }
      : null,
    crm: crmCounts,
    social: {
      posts: socialCounts,
      accounts: accountsSnap.size,
    },
    tasks: {
      sampled: tasks.length,
      blockedOrAwaiting: blockedTasks.length,
      byKind,
      rows: blockedTasks,
    },
    safety: 'Read-only approval queue gather. No task, CRM, social, deploy, env, spend, or destructive mutation performed.',
  }

  if (writeHtml) {
    const html = `<!doctype html><meta charset="utf-8"><title>PiB Approval Queue</title><style>body{font-family:system-ui,sans-serif;margin:32px;color:#111}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;vertical-align:top;text-align:left}th{background:#f4f4f4}</style><h1>PiB Approval Queue</h1><p>${escapeHtml(result.checkedAt)} | ${escapeHtml(orgId)}</p><table><thead><tr><th>Kind</th><th>Task</th><th>Status</th><th>Recommendation</th></tr></thead><tbody>${blockedTasks.map((task) => `<tr><td>${escapeHtml(task.kind)}</td><td>${escapeHtml(task.title)}<br><code>${escapeHtml(task.id)}</code></td><td>${escapeHtml(task.agentStatus)} / ${escapeHtml(task.columnId)}</td><td>${escapeHtml(task.recommendation)}</td></tr>`).join('')}</tbody></table>`
    const file = path.join(os.tmpdir(), `pib-approval-queue-${orgId}-${Date.now()}.html`)
    await fs.writeFile(file, html)
    result.tempHtml = file
  }

  console.log(JSON.stringify(result, null, 2))
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
