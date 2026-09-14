#!/usr/bin/env node
'use strict'

const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const http = require('node:http')
const https = require('node:https')
const { spawn } = require('node:child_process')

const CONFIG_DIR = process.env.PIB_CONFIG_DIR || path.join(os.homedir(), '.config', 'partnersinbiz')
const CREDENTIALS_PATH = path.join(CONFIG_DIR, 'credentials.json')
const DEFAULT_API_BASE = process.env.PIB_API_BASE || 'https://partnersinbiz.online'

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'))
  } catch {
    return null
  }
}

function writeCredentials(data) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 })
  fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify(data, null, 2) + '\n', { mode: 0o600 })
}

function loadCredentials() {
  const envToken = process.env.PIB_ACCESS_TOKEN || process.env.PIB_USER_TOKEN || ''
  const stored = readJson(CREDENTIALS_PATH) || {}
  return {
    apiBase: (process.env.PIB_API_BASE || stored.apiBase || DEFAULT_API_BASE).replace(/\/+$/, ''),
    accessToken: envToken || stored.accessToken || '',
    refreshToken: stored.refreshToken || '',
    expiresAt: stored.expiresAt || '',
    orgId: process.env.PIB_ORG_ID || stored.orgId || '',
    user: stored.user || null,
  }
}

function requestJson(url, options = {}, body) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url)
    const lib = parsed.protocol === 'http:' ? http : https
    const req = lib.request({
      method: options.method || 'GET',
      hostname: parsed.hostname,
      port: parsed.port || undefined,
      path: parsed.pathname + parsed.search,
      headers: {
        Accept: 'application/json',
        ...(body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.headers || {}),
      },
    }, (res) => {
      const chunks = []
      res.on('data', (chunk) => chunks.push(chunk))
      res.on('end', () => {
        const text = Buffer.concat(chunks).toString('utf8')
        let json = null
        try { json = text ? JSON.parse(text) : null } catch { json = { raw: text } }
        resolve({ status: res.statusCode || 0, json, text })
      })
    })
    req.on('error', reject)
    if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body))
    req.end()
  })
}

function unwrap(payload) {
  if (!payload || typeof payload !== 'object') return payload
  return payload.data ?? payload
}

function openBrowser(url) {
  const cmd = process.platform === 'darwin' ? 'open' : process.platform === 'win32' ? 'cmd' : 'xdg-open'
  const args = process.platform === 'win32' ? ['/c', 'start', '', url] : [url]
  spawn(cmd, args, { detached: true, stdio: 'ignore' }).unref()
}

async function refreshIfNeeded(creds) {
  if (!creds.refreshToken) return creds
  const expiresAt = Date.parse(creds.expiresAt || '')
  if (Number.isFinite(expiresAt) && expiresAt - Date.now() > 60 * 1000 && creds.accessToken) return creds
  const res = await requestJson(`${creds.apiBase}/api/v1/oauth/token`, { method: 'POST' }, {
    grant_type: 'refresh_token',
    refresh_token: creds.refreshToken,
  })
  const data = unwrap(res.json)
  if (res.status >= 400 || !data?.access_token) {
    throw new Error(data?.error_description || data?.error || 'Refresh failed. Run pib-skills login again.')
  }
  const next = {
    ...creds,
    accessToken: data.access_token,
    refreshToken: data.refresh_token || creds.refreshToken,
    expiresAt: new Date(Date.now() + (Number(data.expires_in) || 3600) * 1000).toISOString(),
    orgId: data.org_id || creds.orgId,
  }
  writeCredentials(next)
  return next
}

async function cmdLogin() {
  const apiBase = DEFAULT_API_BASE.replace(/\/+$/, '')
  const started = await requestJson(`${apiBase}/api/v1/oauth/device/code`, { method: 'POST' }, {
    client_id: 'pib-skills-cli',
    client_label: process.env.PIB_CLIENT_LABEL || 'pib-skills CLI',
  })
  const data = unwrap(started.json)
  if (started.status >= 400 || !data?.device_code) {
    throw new Error(data?.error_description || data?.error || 'Could not start device login')
  }
  const verifyUrl = data.verification_uri_complete || `${data.verification_uri}?code=${encodeURIComponent(data.user_code)}`
  console.log(`Open this page and approve the agent:\n  ${verifyUrl}`)
  console.log(`User code: ${data.user_code}`)
  try { openBrowser(verifyUrl) } catch { /* ignore */ }

  const interval = Math.max(Number(data.interval) || 5, 5)
  const deadline = Date.now() + (Number(data.expires_in) || 600) * 1000
  while (Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, interval * 1000))
    const tokenRes = await requestJson(`${apiBase}/api/v1/oauth/token`, { method: 'POST' }, {
      grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
      device_code: data.device_code,
    })
    const tokenData = unwrap(tokenRes.json)
    const error = tokenData?.error || tokenRes.json?.error
    if (error === 'authorization_pending') continue
    if (error === 'slow_down') {
      await new Promise((resolve) => setTimeout(resolve, 5000))
      continue
    }
    if (tokenRes.status >= 400 || !tokenData?.access_token) {
      throw new Error(tokenData?.error_description || error || 'Login failed')
    }
    const creds = {
      apiBase,
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token,
      expiresAt: new Date(Date.now() + (Number(tokenData.expires_in) || 3600) * 1000).toISOString(),
      orgId: tokenData.org_id || '',
      user: null,
    }
    writeCredentials(creds)
    const who = await cmdWhoami(true)
    console.log(`Signed in as ${who.email || who.uid} in ${who.orgName || who.orgId}.`)
    return
  }
  throw new Error('Timed out waiting for approval')
}

function cmdLogout() {
  if (fs.existsSync(CREDENTIALS_PATH)) fs.unlinkSync(CREDENTIALS_PATH)
  console.log('Signed out. Local credentials removed.')
}

async function cmdWhoami(quiet = false) {
  let creds = loadCredentials()
  if (!creds.accessToken) throw new Error('Not signed in. Run pib-skills login.')
  creds = await refreshIfNeeded(creds)
  const res = await requestJson(`${creds.apiBase}/api/v1/oauth/whoami`, {
    headers: {
      Authorization: `Bearer ${creds.accessToken}`,
      ...(creds.orgId ? { 'X-Org-Id': creds.orgId } : {}),
    },
  })
  const data = unwrap(res.json)
  if (res.status >= 400) throw new Error(data?.error_description || data?.error || 'whoami failed')
  writeCredentials({ ...creds, orgId: data.orgId || creds.orgId, user: data })
  if (!quiet) {
    console.log(JSON.stringify(data, null, 2))
  }
  return data
}

function cmdStatus() {
  const creds = loadCredentials()
  console.log(`credentials: ${CREDENTIALS_PATH}`)
  console.log(`apiBase: ${creds.apiBase}`)
  console.log(`signedIn: ${Boolean(creds.accessToken)}`)
  console.log(`orgId: ${creds.orgId || '(none)'}`)
  console.log(`expiresAt: ${creds.expiresAt || '(none)'}`)
}

async function main() {
  const cmd = process.argv[2] || 'help'
  try {
    if (cmd === 'login') await cmdLogin()
    else if (cmd === 'logout') cmdLogout()
    else if (cmd === 'whoami') await cmdWhoami(false)
    else if (cmd === 'status') cmdStatus()
    else {
      console.log('Usage: pib-auth login|logout|whoami|status')
      process.exit(cmd === 'help' || cmd === '--help' ? 0 : 1)
    }
  } catch (err) {
    console.error(err instanceof Error ? err.message : String(err))
    process.exit(1)
  }
}

main()
