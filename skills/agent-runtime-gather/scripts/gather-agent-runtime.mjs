#!/usr/bin/env node
import { createRequire } from 'node:module'
import path from 'node:path'
import os from 'node:os'
import fs from 'node:fs/promises'

const appRequire = createRequire(path.join(process.cwd(), 'package.json'))
const dotenv = appRequire('dotenv')
const { initializeApp, getApps, cert } = appRequire('firebase-admin/app')
const { getFirestore } = appRequire('firebase-admin/firestore')

const args = process.argv.slice(2)
function arg(name, fallback = '') {
  const flag = `--${name}`
  const index = args.indexOf(flag)
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

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

async function main() {
  const [agentsSnap, tasksSnap, runsSnap, convSnap] = await Promise.all([
    db.collection('agent_team').get(),
    db.collection('tasks').where('orgId', '==', orgId).get(),
    db.collection('hermes_runs').orderBy('createdAt', 'desc').limit(120).get()
      .catch(() => db.collection('hermes_runs').limit(120).get()),
    db.collection('conversations').doc(conversationId).get(),
  ])

  const agents = agentsSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
  const tasks = tasksSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
  const runs = runsSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() }))

  const agentRows = agents
    .map((agent) => ({
      id: agent.id,
      name: agent.name || agent.displayName || agent.id,
      enabled: agent.enabled === true,
      role: agent.role || agent.kind || null,
      hasBaseUrl: Boolean(agent.baseUrl),
      skillCount: Array.isArray(agent.skills)
        ? agent.skills.length
        : Array.isArray(agent.installedSkills)
          ? agent.installedSkills.length
          : null,
      updatedAt: ts(agent.updatedAt),
    }))
    .sort((a, b) => a.id.localeCompare(b.id))

  const taskByAgent = {}
  for (const task of tasks) {
    const agentId = task.assigneeAgentId || task.assignedAgentId || task.agentId || 'unassigned'
    taskByAgent[agentId] ??= { total: 0, awaiting: 0, blocked: 0, inProgress: 0, review: 0, done: 0, latest: [] }
    const row = taskByAgent[agentId]
    const status = lower(task.agentStatus || task.status)
    const column = lower(task.columnId)
    row.total += 1
    if (status === 'awaiting-input') row.awaiting += 1
    if (status === 'blocked' || column === 'blocked') row.blocked += 1
    if (status === 'in-progress' || column === 'in_progress') row.inProgress += 1
    if (column === 'review') row.review += 1
    if (status === 'done' || column === 'done') row.done += 1
    row.latest.push({
      id: task.id,
      title: task.title || task.name || '',
      agentStatus: task.agentStatus || null,
      columnId: task.columnId || null,
      updatedAt: ts(task.updatedAt),
    })
  }
  for (const row of Object.values(taskByAgent)) {
    row.latest = row.latest.sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt))).slice(0, 5)
  }

  const runCounts = runs.reduce((acc, run) => {
    const status = run.status || run.state || 'unknown'
    acc[status] = (acc[status] || 0) + 1
    return acc
  }, {})
  const activeStatuses = new Set(['started', 'pending', 'running'])
  const stuckRuns = runs
    .filter((run) => activeStatuses.has(lower(run.status || run.state)))
    .map((run) => ({
      id: run.id,
      status: run.status || run.state || null,
      agentId: run.agentId || run.dispatchAgentId || run.profile || null,
      conversationId: run.conversationId || run.metadata?.conversationId || null,
      messageId: run.messageId || run.metadata?.messageId || null,
      createdAt: ts(run.createdAt),
      updatedAt: ts(run.updatedAt),
    }))
    .slice(0, 40)

  const approvalTasks = tasks
    .filter((task) => lower(task.agentStatus) === 'awaiting-input' || lower(task.columnId) === 'blocked')
    .map((task) => ({
      id: task.id,
      title: task.title || task.name || '',
      assigneeAgentId: task.assigneeAgentId || null,
      agentStatus: task.agentStatus || null,
      columnId: task.columnId || null,
      updatedAt: ts(task.updatedAt),
    }))
    .sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)))

  const result = {
    checkedAt: new Date().toISOString(),
    orgId,
    conversationId,
    conversation: convSnap.exists
      ? {
          messageCount: convSnap.get('messageCount') ?? null,
          lastMessageId: convSnap.get('lastMessageId') ?? null,
        }
      : null,
    agents: {
      total: agentRows.length,
      enabled: agentRows.filter((agent) => agent.enabled).length,
      missingBaseUrl: agentRows.filter((agent) => !agent.hasBaseUrl).map((agent) => agent.id),
      rows: agentRows,
    },
    tasks: {
      total: tasks.length,
      byAgent: taskByAgent,
      approvalTasks: approvalTasks.slice(0, 30),
    },
    hermesRuns: {
      sampled: runs.length,
      counts: runCounts,
      activeOrStuck: stuckRuns.length,
      stuckRuns,
    },
    safety: 'Read-only agent runtime gather. No agent config, task, Hermes run, release, env, or destructive mutation performed.',
  }

  if (writeHtml) {
    const rows = [
      ['Agents enabled', `${result.agents.enabled}/${result.agents.total}`],
      ['Tasks sampled', result.tasks.total],
      ['Approval/blocked tasks', result.tasks.approvalTasks.length],
      ['Hermes runs sampled', result.hermesRuns.sampled],
      ['Started/pending/running runs', result.hermesRuns.activeOrStuck],
    ]
    const html = `<!doctype html><meta charset="utf-8"><title>PiB Agent Runtime Snapshot</title><style>body{font-family:system-ui,sans-serif;margin:32px;color:#111}table{border-collapse:collapse;min-width:640px}td,th{border:1px solid #ddd;padding:8px 10px;text-align:left;vertical-align:top}th{background:#f4f4f4}</style><h1>PiB Agent Runtime Snapshot</h1><p>${escapeHtml(result.checkedAt)} | ${escapeHtml(orgId)}</p><table><tbody>${rows.map(([k,v])=>`<tr><td>${escapeHtml(k)}</td><td>${escapeHtml(v)}</td></tr>`).join('')}</tbody></table><h2>Active/stuck runs</h2><ul>${stuckRuns.slice(0,20).map((run)=>`<li>${escapeHtml(run.id)} — ${escapeHtml(run.status)} — ${escapeHtml(run.agentId)} — ${escapeHtml(run.createdAt)}</li>`).join('')}</ul>`
    const file = path.join(os.tmpdir(), `pib-agent-runtime-${orgId}-${Date.now()}.html`)
    await fs.writeFile(file, html)
    result.tempHtml = file
  }

  console.log(JSON.stringify(result, null, 2))
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
