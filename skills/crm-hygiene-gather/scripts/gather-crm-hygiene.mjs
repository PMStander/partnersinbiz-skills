#!/usr/bin/env node
import { createRequire } from 'node:module'
import path from 'node:path'
import os from 'node:os'
import fs from 'node:fs/promises'

const appRequire = createRequire(path.join(process.cwd(), 'package.json'))
const dotenv = appRequire('dotenv')
const { initializeApp, getApps, cert } = appRequire('firebase-admin/app')
const { getFirestore } = appRequire('firebase-admin/firestore')
const { activeRows, emailDuplicateGroups } = appRequire('./scripts/crm-gather-active-records')

const args = process.argv.slice(2)
function arg(name, fallback = '') {
  const flag = `--${name}`
  const index = args.indexOf(flag)
  return index >= 0 ? args[index + 1] ?? fallback : fallback
}
const orgId = arg('org', 'pib-platform-owner')
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
const text = (value) => typeof value === 'string' ? value.trim() : ''
const lower = (value) => text(value).toLowerCase()
const amount = (deal) => Number(deal.value ?? deal.amount ?? deal.dealValue ?? 0)

function isOpenDeal(deal) {
  const status = lower(deal.status)
  const stage = lower(deal.stage || deal.stageId)
  return !['won', 'lost', 'closed', 'closed_won', 'closed_lost'].includes(status)
    && !['won', 'lost', 'closed', 'closed_won', 'closed_lost'].includes(stage)
}

function isProposalDeal(deal) {
  return lower(deal.stage || deal.stageId).includes('proposal')
    || lower(deal.name || deal.title).includes('proposal')
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

async function main() {
  const [contactsSnap, companiesSnap, dealsSnap, tasksSnap] = await Promise.all([
    db.collection('contacts').where('orgId', '==', orgId).get(),
    db.collection('companies').where('orgId', '==', orgId).get(),
    db.collection('deals').where('orgId', '==', orgId).get(),
    db.collection('tasks').where('orgId', '==', orgId).get(),
  ])

  const contacts = activeRows(contactsSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() })))
  const companies = activeRows(companiesSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() })))
  const deals = activeRows(dealsSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() })))
  const tasks = activeRows(tasksSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() })))
  const duplicates = emailDuplicateGroups(contacts)
  const openDeals = deals.filter(isOpenDeal)
  const proposalDeals = deals.filter(isProposalDeal)
  const proposalGaps = proposalDeals
    .filter((deal) => amount(deal) <= 0 || !deal.expectedCloseDate)
    .map((deal) => ({
      id: deal.id,
      name: deal.name || deal.title || '',
      value: amount(deal) > 0 ? amount(deal) : null,
      expectedCloseDate: ts(deal.expectedCloseDate),
      stage: deal.stage || deal.stageId || null,
    }))
  const approvals = tasks
    .filter((task) => ['awaiting-input', 'blocked'].includes(lower(task.agentStatus || task.status || task.columnId)) || lower(task.columnId) === 'blocked')
    .map((task) => ({
      id: task.id,
      title: task.title || task.name || '',
      status: task.status || null,
      agentStatus: task.agentStatus || null,
      columnId: task.columnId || null,
      assigneeAgentId: task.assigneeAgentId || null,
      updatedAt: ts(task.updatedAt),
    }))

  const result = {
    checkedAt: new Date().toISOString(),
    orgId,
    counts: {
      contacts: contacts.length,
      companies: companies.length,
      deals: deals.length,
      openDeals: openDeals.length,
      proposalDeals: proposalDeals.length,
      approvalGates: approvals.length,
    },
    hygiene: {
      contactsMissingCompany: contacts.filter((contact) => !contact.companyId && !contact.company).length,
      contactsMissingOwner: contacts.filter((contact) => !contact.ownerId && !contact.assignedTo).length,
      companiesMissingWebsite: companies.filter((company) => !company.website && !company.domain).length,
      duplicateEmailGroups: duplicates.length,
      duplicateEmailSamples: duplicates.slice(0, 10),
      proposalDealsMissingValueOrDate: proposalGaps,
    },
    approvalGates: approvals.slice(0, 40),
    safety: 'Read-only CRM hygiene gather. No CRM, sales, social, approval, billing, or external mutation performed.',
  }

  if (writeHtml) {
    const rows = [
      ['Contacts', result.counts.contacts],
      ['Contacts missing company', result.hygiene.contactsMissingCompany],
      ['Contacts missing owner', result.hygiene.contactsMissingOwner],
      ['Companies missing website/domain', result.hygiene.companiesMissingWebsite],
      ['Duplicate email groups', result.hygiene.duplicateEmailGroups],
      ['Open deals', result.counts.openDeals],
      ['Proposal deal gaps', result.hygiene.proposalDealsMissingValueOrDate.length],
      ['Approval gates', result.counts.approvalGates],
    ]
    const html = `<!doctype html><meta charset="utf-8"><title>PiB CRM Hygiene Snapshot</title><style>body{font-family:system-ui,sans-serif;margin:32px;color:#111}table{border-collapse:collapse;min-width:520px}td,th{border:1px solid #ddd;padding:8px 10px;text-align:left}th{background:#f4f4f4}</style><h1>PiB CRM Hygiene Snapshot</h1><p>${escapeHtml(result.checkedAt)} | ${escapeHtml(orgId)}</p><table><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>${rows.map(([k,v])=>`<tr><td>${escapeHtml(k)}</td><td>${escapeHtml(v)}</td></tr>`).join('')}</tbody></table><h2>Proposal deal gaps</h2><ul>${proposalGaps.map((deal)=>`<li>${escapeHtml(deal.name)} — ${escapeHtml(deal.id)} — value ${escapeHtml(deal.value ?? 'missing')} — close ${escapeHtml(deal.expectedCloseDate ?? 'missing')}</li>`).join('')}</ul>`
    const file = path.join(os.tmpdir(), `pib-crm-hygiene-${orgId}-${Date.now()}.html`)
    await fs.writeFile(file, html)
    result.tempHtml = file
  }

  console.log(JSON.stringify(result, null, 2))
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
