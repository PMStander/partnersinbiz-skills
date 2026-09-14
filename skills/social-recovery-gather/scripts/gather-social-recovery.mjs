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
const campaignId = arg('campaign', '')
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

function postPlatform(post) {
  return post.platform || post.platforms?.[0] || 'unknown'
}

function postAccountId(post) {
  return post.accountId || post.socialAccountId || post.accountIds?.[0] || post.accounts?.[0]?.id || null
}

function postError(post) {
  return text(post.error || post.failureReason || post.lastError || post.publishError || post.metadata?.error || post.providerError)
}

function classifyFailure(post) {
  const error = lower(postError(post))
  if (!postAccountId(post)) return 'missing-account-link'
  if (/expired|token|oauth|authenticate|reconnect|not publishable|401|403/.test(error)) return 'auth-or-scope'
  if (/media|upload|image|video|not ready|9007/.test(error)) return 'media'
  if (/rate|limit|429/.test(error)) return 'rate-limit'
  if (!error) return 'unknown-no-error'
  return 'provider-error'
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

async function main() {
  const [postsSnap, accountsSnap] = await Promise.all([
    db.collection('social_posts').where('orgId', '==', orgId).get(),
    db.collection('social_accounts').where('orgId', '==', orgId).get(),
  ])
  const posts = postsSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
  const accounts = accountsSnap.docs.map((doc) => ({ id: doc.id, ...doc.data() }))
  const accountById = Object.fromEntries(accounts.map((account) => [account.id, account]))
  const failed = posts.filter((post) => post.status === 'failed')
  const failedRows = failed.map((post) => {
    const accountId = postAccountId(post)
    const account = accountId ? accountById[accountId] : null
    return {
      id: post.id,
      platform: postPlatform(post),
      accountId,
      accountStatus: account?.status ?? null,
      accountName: account?.displayName || account?.username || null,
      classification: classifyFailure(post),
      error: postError(post),
      updatedAt: ts(post.updatedAt),
      createdAt: ts(post.createdAt),
    }
  })
  const counts = posts.reduce((acc, post) => {
    acc[post.status || 'unknown'] = (acc[post.status || 'unknown'] || 0) + 1
    return acc
  }, {})
  const failedByPlatform = failedRows.reduce((acc, row) => {
    acc[row.platform] = (acc[row.platform] || 0) + 1
    return acc
  }, {})
  const failedByClass = failedRows.reduce((acc, row) => {
    acc[row.classification] = (acc[row.classification] || 0) + 1
    return acc
  }, {})
  const defaultCampaignIds = [
    'hzq7AmVKNTFxNTwb9IVD',
    'HfTT2WysSRgYkxwF8iTz',
    'B1Si4FasTPHpEkm7odry',
    'AO2QjwUqIjJqrHkHINpG',
    'dawDHBYlHFGguGokDG5c',
    'TidCRwMOYoLU0NH5QfP5',
    'Jp26HevoJmL253eTuMfS',
  ]
  const campaignPosts = posts.filter((post) => (
    campaignId
      ? post.campaignId === campaignId || post.campaign?.id === campaignId || defaultCampaignIds.includes(post.id)
      : defaultCampaignIds.includes(post.id)
  ))
  const campaign = campaignPosts.map((post) => {
    const accountId = postAccountId(post)
    const account = accountId ? accountById[accountId] : null
    return {
      id: post.id,
      platform: postPlatform(post),
      status: post.status,
      accountId,
      accountStatus: account?.status ?? null,
      accountName: account?.displayName || account?.username || null,
      mediaCount: Array.isArray(post.media) ? post.media.length : 0,
      scheduledAt: ts(post.scheduledAt),
      scheduledFor: ts(post.scheduledFor),
      approvedAt: ts(post.approvedAt),
      publishedAt: ts(post.publishedAt),
    }
  }).sort((a, b) => a.platform.localeCompare(b.platform))

  const result = {
    checkedAt: new Date().toISOString(),
    orgId,
    campaignId: campaignId || null,
    counts,
    accounts: accounts.map((account) => ({
      id: account.id,
      platform: account.platform,
      status: account.status,
      displayName: account.displayName || account.username || '',
      isDefault: account.isDefault === true,
    })),
    failed: {
      total: failedRows.length,
      byPlatform: failedByPlatform,
      byClassification: failedByClass,
      samples: failedRows.slice(0, 40),
    },
    campaign,
    safety: 'Read-only social recovery gather. No submit, approval, schedule, publish, retry, reconnect, env, spend, or destructive action performed.',
  }

  if (writeHtml) {
    const html = `<!doctype html><meta charset="utf-8"><title>PiB Social Recovery Snapshot</title><style>body{font-family:system-ui,sans-serif;margin:32px;color:#111}table{border-collapse:collapse;min-width:720px}td,th{border:1px solid #ddd;padding:8px 10px;text-align:left;vertical-align:top}th{background:#f4f4f4}</style><h1>PiB Social Recovery Snapshot</h1><p>${escapeHtml(result.checkedAt)} | ${escapeHtml(orgId)}</p><h2>Failed by platform</h2><table><tbody>${Object.entries(failedByPlatform).map(([k,v])=>`<tr><td>${escapeHtml(k)}</td><td>${escapeHtml(v)}</td></tr>`).join('')}</tbody></table><h2>Failed samples</h2><table><thead><tr><th>ID</th><th>Platform</th><th>Class</th><th>Error</th></tr></thead><tbody>${failedRows.slice(0,40).map((row)=>`<tr><td>${escapeHtml(row.id)}</td><td>${escapeHtml(row.platform)}</td><td>${escapeHtml(row.classification)}</td><td>${escapeHtml(row.error)}</td></tr>`).join('')}</tbody></table>`
    const file = path.join(os.tmpdir(), `pib-social-recovery-${orgId}-${Date.now()}.html`)
    await fs.writeFile(file, html)
    result.tempHtml = file
  }

  console.log(JSON.stringify(result, null, 2))
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
