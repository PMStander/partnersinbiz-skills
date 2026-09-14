#!/usr/bin/env node
/**
 * Lightweight contract checks for the system skills pack.
 * Ensures golden payloads exist and invalid examples are documented.
 */
import { readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const repoRoot = join(root, '..', '..')
const manifest = JSON.parse(readFileSync(join(root, 'manifest.json'), 'utf8'))

let failed = 0
function check(cond, msg) {
  if (!cond) {
    console.error(`FAIL: ${msg}`)
    failed += 1
  } else {
    console.log(`ok: ${msg}`)
  }
}

check(typeof manifest.packVersion === 'string' && manifest.packVersion.length > 0, 'packVersion set')
check(manifest.tiers?.core?.skills?.includes('system-auth'), 'core includes system-auth')
check(manifest.tiers?.core?.skills?.includes('client-documents'), 'core includes client-documents')
check(manifest.tiers?.core?.skills?.includes('agent-runtime-ops'), 'core includes agent-runtime-ops')
check(manifest.tiers?.core?.skills?.includes('reports'), 'core includes reports')
check(manifest.tiers?.core?.skills?.includes('daily-workflow'), 'core includes daily-workflow')
check(manifest.tiers?.core?.skills?.includes('pib-bot-teams'), 'core includes pib-bot-teams')
check(manifest.tiers?.core?.skills?.includes('pib-chat-canvas'), 'core includes pib-chat-canvas')
check(manifest.tiers?.core?.skills?.includes('pib-routines'), 'core includes pib-routines')

const dailySkillPath = join(root, 'skills/daily-workflow/SKILL.md')
const dailyRepoPath = join(repoRoot, '.claude/skills/daily-workflow/SKILL.md')
check(existsSync(dailySkillPath), 'daily-workflow pack skill exists')
check(existsSync(dailyRepoPath), 'daily-workflow repo skill exists')
if (existsSync(dailySkillPath) && existsSync(dailyRepoPath)) {
  const dailyPack = readFileSync(dailySkillPath, 'utf8')
  const dailyRepo = readFileSync(dailyRepoPath, 'utf8')
  check(dailyPack.includes('version: 1.2.0'), 'daily-workflow version is 1.2.0')
  check(dailyPack === dailyRepo, 'daily-workflow repo and pack copies match')
  check(!dailyPack.includes('rm -rf'), 'daily-workflow forbids destructive cleanup commands')
  check(!dailyPack.includes('git add -A'), 'daily-workflow forbids blind stage-all')
}

const teamsSkillPath = join(root, 'skills/pib-bot-teams/SKILL.md')
const teamsRepoPath = join(repoRoot, '.claude/skills/pib-bot-teams/SKILL.md')
check(existsSync(teamsSkillPath), 'pib-bot-teams pack skill exists')
check(existsSync(teamsRepoPath), 'pib-bot-teams repo skill exists')
if (existsSync(teamsSkillPath) && existsSync(teamsRepoPath)) {
  const teamsPack = readFileSync(teamsSkillPath, 'utf8')
  const teamsRepo = readFileSync(teamsRepoPath, 'utf8')
  check(teamsPack === teamsRepo, 'pib-bot-teams repo and pack copies match')
  check(teamsPack.includes('Address teammates with `@handle`'), 'pib-bot-teams documents @handle addressing')
  check(teamsPack.includes('message_agent'), 'pib-bot-teams documents message_agent')
  check(teamsPack.includes('maxRounds'), 'pib-bot-teams documents maxRounds')
  check(teamsPack.includes('maxMessages'), 'pib-bot-teams documents maxMessages')
  check(teamsPack.includes('maxMembers'), 'pib-bot-teams documents maxMembers')
  check(teamsPack.includes('Desktop-only'), 'pib-bot-teams documents Desktop-only @user escalation')
  check(teamsPack.includes('needsYou'), 'pib-bot-teams documents PiB needsYou mention parser')
  check(teamsPack.includes('Never put API keys, tokens, passwords, `.env` values, session cookies, or file contents'), 'pib-bot-teams forbids credentials and file contents in DMs')
  check(teamsPack.includes('report the typed reason **exactly** as received'), 'pib-bot-teams reports failure reasons verbatim')
  check(teamsPack.includes('hermes-bots-groups'), 'pib-bot-teams persists rooms via hermes-bots-groups')
  check(teamsPack.includes('profiles.configure'), 'pib-bot-teams persists rooms via profiles.configure')
  check(teamsPack.includes('groups.*'), 'pib-bot-teams forbids hosted groups.*')
}

const canvasSkillPath = join(root, 'skills/pib-chat-canvas/SKILL.md')
const canvasRepoPath = join(repoRoot, '.claude/skills/pib-chat-canvas/SKILL.md')
check(existsSync(canvasSkillPath), 'pib-chat-canvas pack skill exists')
check(existsSync(canvasRepoPath), 'pib-chat-canvas repo skill exists')
if (existsSync(canvasSkillPath) && existsSync(canvasRepoPath)) {
  const canvasPack = readFileSync(canvasSkillPath, 'utf8')
  const canvasRepo = readFileSync(canvasRepoPath, 'utf8')
  check(canvasPack === canvasRepo, 'pib-chat-canvas repo and pack copies match')
  check(canvasPack.includes('```pib:chart'), 'pib-chat-canvas documents pib:chart')
  check(canvasPack.includes('Never put secrets or raw HTML from a web page into `pib:html`'), 'pib-chat-canvas forbids secrets and scraped HTML')
}

const routinesSkillPath = join(root, 'skills/pib-routines/SKILL.md')
const routinesRepoPath = join(repoRoot, '.claude/skills/pib-routines/SKILL.md')
check(existsSync(routinesSkillPath), 'pib-routines pack skill exists')
check(existsSync(routinesRepoPath), 'pib-routines repo skill exists')
if (existsSync(routinesSkillPath) && existsSync(routinesRepoPath)) {
  const routinesPack = readFileSync(routinesSkillPath, 'utf8')
  const routinesRepo = readFileSync(routinesRepoPath, 'utf8')
  check(routinesPack === routinesRepo, 'pib-routines repo and pack copies match')
  check(routinesPack.includes('botRoutinesEnabled'), 'pib-routines documents botRoutinesEnabled')
}

const policyPath = join(repoRoot, 'config/agent-skill-policy.json')
check(existsSync(policyPath), 'agent-skill-policy.json present for lockstep')
if (existsSync(policyPath)) {
  const policy = JSON.parse(readFileSync(policyPath, 'utf8'))
  check(
    policy.catalogVersion === manifest.catalogVersion,
    `catalogVersion lockstep policy=${policy.catalogVersion} pack=${manifest.catalogVersion}`,
  )
}

for (const [name, meta] of Object.entries(manifest.skills || {})) {
  const skillMd = join(root, 'skills', name, 'SKILL.md')
  check(existsSync(skillMd), `skill file exists: ${name}`)
  if (Array.isArray(meta.contracts)) {
    for (const rel of meta.contracts) {
      check(existsSync(join(root, rel)), `contract exists: ${rel}`)
    }
  }
}

const valid = JSON.parse(readFileSync(join(root, 'contracts/client-documents/version-payload.valid.json'), 'utf8'))
check(Array.isArray(valid.blocks) && valid.blocks.length >= 1, 'valid version payload has blocks')
check(valid.blocks.every((b) => typeof b.id === 'string' && typeof b.type === 'string'), 'blocks have id+type')
check(valid.blocks.every((b) => typeof b.required === 'boolean'), 'blocks have required boolean')
check(valid.blocks.every((b) => b.display && typeof b.display === 'object'), 'blocks have display object')
check(valid.theme?.palette?.bg && valid.theme?.typography?.heading, 'theme has palette+typography')

const invalid = JSON.parse(readFileSync(join(root, 'contracts/client-documents/version-payload.invalid.json'), 'utf8'))
check(Array.isArray(invalid.cases) && invalid.cases.length >= 1, 'invalid cases documented')

const invoiceValid = JSON.parse(readFileSync(join(root, 'contracts/billing-finance/invoice-create.valid.json'), 'utf8'))
check(Array.isArray(invoiceValid.lineItems) && invoiceValid.lineItems.length >= 1, 'invoice golden has lineItems')
check(typeof invoiceValid.currency === 'string' && invoiceValid.currency.length === 3, 'invoice golden has currency')

const invoiceInvalid = JSON.parse(readFileSync(join(root, 'contracts/billing-finance/invoice-create.invalid.json'), 'utf8'))
check(Array.isArray(invoiceInvalid.cases) && invoiceInvalid.cases.length >= 1, 'invoice invalid cases documented')

const contactValid = JSON.parse(readFileSync(join(root, 'contracts/crm-sales/contact-create.valid.json'), 'utf8'))
check(typeof contactValid.name === 'string' && typeof contactValid.email === 'string', 'contact golden has name+email')
check(!Object.prototype.hasOwnProperty.call(contactValid, 'orgId'), 'contact golden does not put orgId in body')

const contactInvalid = JSON.parse(readFileSync(join(root, 'contracts/crm-sales/contact-create.invalid.json'), 'utf8'))
check(Array.isArray(contactInvalid.cases) && contactInvalid.cases.length >= 1, 'contact invalid cases documented')

if (failed) {
  console.error(`\n${failed} contract check(s) failed`)
  process.exit(1)
}
console.log('\nAll contract checks passed')
