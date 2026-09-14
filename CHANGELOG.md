# Changelog

## 0.2.0 — 2026-09-14

- Publish this pack as the public repo `PMStander/partnersinbiz-skills`.
- Add device OAuth login (`pib-skills login`) and Settings personal tokens so external agents act as the signed-in human.
- Include extra Cowork/Claude skills (gather, marketing/ads, higgsfield, studio, software-development) alongside the original core/growth pack.
- `system-auth` now documents Messages injection **and** external device login. Never use `AI_API_KEY` for interactive work.

## 0.1.11 — 2026-09-03

- Add `pib-bot-teams` (core): teach every managed profile to address teammates
  with `@handle`, choose `message_agent` vs a direct room answer, honour the
  Hermes `botMode.rounds` caps (3 rounds / 10 messages / 6 members), escalate
  with `@user` (Desktop-only; PiB sets `needsYou` from its mention parser),
  never paste credentials or file contents into a DM, and report delivery
  failure reasons verbatim. Rooms persist via `hermes-bots-groups` /
  `profiles.configure`, not hosted `groups.*`. Owner: pip; allowed on every
  platform agent.
- Bump `catalogVersion` to `2026-09-03.system-skills-v0.1.11` so the pack stays
  in lockstep with `config/agent-skill-policy.json`.

## 0.1.10 — 2026-09-03

- Add `pib-chat-canvas` (core): teach every managed profile to emit `pib:chart`,
  `pib:mermaid`, `pib:math`, and `pib:html` fences plus working-directory file
  references so Messages can parse canvas parts. Limits come from
  `lib/chat/parts.ts` `PART_LIMITS`. Owner: pip; allowed on every platform agent
  and marketplace public packs.
- Bump `catalogVersion` to `2026-09-03.system-skills-v0.1.10` so the pack stays
  in lockstep with `config/agent-skill-policy.json`.

## 0.1.9 — 2026-08-26

- Correct `social-media-manager` LinkedIn company-page note: keep the existing
  LinkedIn app, flip `LINKEDIN_CMA_ENABLED`, then reconnect. Do not swap
  `LINKEDIN_CLIENT_ID` / `LINKEDIN_CLIENT_SECRET` and do not invent a second app.
- Bump `catalogVersion` to `2026-08-10.system-skills-v0.1.9` so the pack stays
  in lockstep with `config/agent-skill-policy.json`.

## 0.1.8 — 2026-08-08

- Add `impeccable-design-discipline` (growth): wrap the Impeccable methodology
  (Apache 2.0, pbakaus/impeccable) as a PiB agent skill — Layer 1, zero platform
  changes. Named design command vocabulary (polish, typeset, layout, colorize,
  audit, critique, harden, distill, clarify, bolder, quieter, overdrive,
  delight, animate, optimize, onboard, adapt, shape, init, document, extract,
  live), per-client design context files (PRODUCT.md/DESIGN.md equivalent in
  wiki/Research via templates/design-context.md), and the deterministic
  anti-slop detector as a runnable check (`npx -y impeccable detect <path|url>
  --json`, exit codes 0/2; references/detector-cli.md). Applied to every web
  task on our site, client sites, and Studio artifacts. Owner: theo; allowed on
  the 9 web-capable agents (data, docs, maya, pip, qa-release, sage, seo,
  support, theo).

## 0.1.7 — 2026-08-05

- Add `browser-agent` (growth): drive the workbench browser (headless Chrome
  over loopback CDP) from Messages — accessibility-tree text snapshots with
  stable @eN refs, click-by-ref, JS dialog handling, console ring, driver
  arbitration (slice 2 attach), private-network guard, `X-Agent-Actor` header
  requirement. Mirrors the Hermes Desktop in-app browser pattern.

## 0.1.6 — 2026-08-04

- Add `workflow-graph-operator` (core): day-to-day Workflow Graph usage for pip/theo/nora/qa-release.
- Residual diagnosis remains on profile skill `pib-workflow-graph-operations`.

## 0.1.5 — 2026-07-30

- Add canonical `daily-workflow` v1.2.0 to the core Partners in Biz system skill pack.
- Allowlist the skill for all 12 managed agents and include it in every linked/client agent skill-pack artifact.
- Reconcile natural-language “start day” and “end the day” behavior with live workspace resolution, repository-specific git rules, task/wiki evidence, and verified process handling.
- Remove the unsafe legacy assumptions that routine closeout should blindly stage all files or delete dependencies and build artifacts.
- Add policy, pack, linked-runtime, contract, installer, and drift coverage for all-agent and client delivery.

## 0.1.2 — 2026-07-23

- Deepen three stub growth skills into route-mapped skills (no v0.1.2 tag/release
  existed yet at time of edit, so this stays under 0.1.2 rather than bumping):
  `video-editor-ops` (24 `app/api/v1/video-editor/**` route files: projects,
  render-jobs, transcripts/translate, tts, reframe, captions/generate,
  media/beats, stock search/import, luts, templates/resolve, media-previews,
  proxy-ledger), `life-os-ops` (`app/api/v1/life-os/**` + admin retention:
  check-ins, coach, experiments, reminders, reviews), and `llm-providers-ops`
  (`app/api/v1/llm-providers/**`: connections CRUD + sync, device-code OAuth
  for xAI/Codex). Each now has a real route map, agent workflows with a
  write→GET read-back success gate, and cross-references; manifest summaries
  updated to match.
- Add golden contracts for billing invoice create + CRM contact create; verify-contracts now enforces policy↔pack catalogVersion lockstep and new core skills
- Deepen conversations-runtime from stub to route-map skill
- Consolidate ~21 `marketing/ads-*` Claude skills into 3 tiered umbrella
  skills: `marketing/ads-strategy` (plan, budget, math, audit, competitor,
  test), `marketing/ads-platforms` (google, meta, linkedin, microsoft,
  tiktok, youtube, apple deep audits), and `marketing/ads-creative` (brand
  DNA, campaign briefs, image generation, photoshoots, landing pages,
  creative-fatigue audit)
- `ads-manager` (PiB platform API skill) unchanged and remains the sole
  ads-related skill in this pack
- `agents.ads` and `agents.maya` runtime policy now load the 3 umbrella
  skills instead of ~21 individual `marketing/ads-*` entries; old skill
  folders remain on disk for one release as reference only
- Split the `platform-ops` mega-skill (~1662 lines) into focused skills:
  `agent-runtime-ops` (Hermes profile links/controls, agent registry/admin,
  agent memory, Loop Engine internals, runtime/provider health, linked
  computers — owner theo, critical risk), `platform-admin-users` (Platform
  Users super-admin CRUD — owner pip, critical risk), and `reports`
  (snapshot + ad-hoc report queries — owner data, medium risk)
- Moved Book Studio / YouTube Studio / Creative Canvas bridge content out of
  `platform-ops` and into the existing `book-studio-ops`, `youtube-studio-ops`,
  and `creative-canvas-ops` stubs, deepening them with real route
  documentation
- Folded FX Rates into `billing-finance` as a short section with an auth
  pointer
- `platform-ops` now opens with a "Related skills" index pointing at the
  splits; trimmed from ~1662 to ~770 lines
- Bump `packVersion`/`catalogVersion` to `0.1.2` alongside the ads-skill
  consolidation wave

## 0.1.1 — 2026-07-23

- Add user-scoped agent delegation token route (`POST /api/v1/agent/delegations`)
- Resolve `pib_dlg_…` Bearer tokens as the acting human in API auth
- Add auth tests and expose delegations in `/api/v1/agent` manifest
- Clarify `system-auth` rollout language: implemented in app code; available after deployment

## 0.1.0 — 2026-07-23

- Initial system skills pack staged at `partnersinbiz-web/packs/pib-system-skills`
- Tiers: `core` (14) + `growth` (10)
- New `system-auth` skill (user-delegation for interactive; system key for cron)
- Client-documents golden + invalid contract fixtures
- `bin/pib-skills` installer/status/verify-contracts
- User-delegation auth spec (`docs/user-delegation-auth.md`)
- Locked decisions: dedicated repo target, env pin + stable channel, core+growth scope
