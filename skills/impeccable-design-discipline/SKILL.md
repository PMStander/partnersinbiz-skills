---
name: impeccable-design-discipline
description: >
  Partners in Biz design discipline for every web task — the Impeccable
  methodology (Apache 2.0, pbakaus/impeccable) wrapped as a PiB agent skill,
  Layer 1 with zero platform changes. Gives agents a named design command
  vocabulary (polish, typeset, layout, colorize, audit, critique, harden,
  distill, clarify, bolder, quieter, overdrive, delight, animate, optimize,
  onboard, adapt, shape, init, document, extract, live), per-client design
  context files (PRODUCT.md/DESIGN.md equivalent in wiki/Research), and the
  deterministic anti-slop detector as a runnable check
  (`npx impeccable detect <path|url> --json`, exit codes 0/2). Use whenever
  the user asks to design, redesign, polish, audit, critique, typeset, layout,
  or colorize any web surface — our own site, client sites, landing pages,
  dashboards, or Studio artifacts — or when any web task should not ship
  generic AI-slop UI. Owner: theo. Apache 2.0 upstream — attribution required.
---
# Impeccable Design Discipline — Partners in Biz Agent Skill (Layer 1)

Wraps the **Impeccable** design-skill pattern (Apache 2.0, by Paul Bakaus /
Renaissance Geek) so every Partners in Biz agent applies the same design
discipline to every web task: our own site, client sites, Studio artifacts,
landing pages, dashboards, and documents. Layer 1 = **zero platform changes**:
the skill adds a command vocabulary, a per-client design-context convention,
and a runnable deterministic detector. No PiB API, schema, or UI changes.

- Upstream: https://github.com/pbakaus/impeccable (Apache 2.0, v4)
- Docs: https://impeccable.style/docs · Cheatsheet: https://impeccable.style/cheatsheet
- Source research: wiki `research/impeccable-impeccable-style-full-functionality-deep-dive-and-pib-implementation-mapping.md` (item `ZTTo7g6CU80u1uUSZvoC`)
- Install: `npx skills add pbakaus/impeccable` (harness builds) or the CLI via `npx -y impeccable` (no install needed)

## When to use this skill (trigger conditions)

Apply this discipline to **any** task that produces or touches a web surface:

- New pages/sections/landing pages, dashboards, portals (our site or a client site)
- Redesigns, brand refreshes, theme changes, component libraries
- Studio artifacts with visual output (social cards, report covers, document themes)
- "Polish", "typeset", "audit", "critique", "make it prettier", "fix this page" requests
- Any UI change to `partnersinbiz-web-development` (portal, marketing site, client sites)
- SEO/content work that includes visual layout decisions

Even when the user did not ask for design work, **any web task ships through the
detector before it is done**. That is the discipline: context first, then
command, then detector, then finish gate.

## The three Layer 1 pillars

### 1. Named design command vocabulary

Impeccable defines 24 named design interventions in 6 categories. PiB agents
use the same vocabulary: when the user asks for one of these, you know exactly
what kind of intervention is meant and which detector scope to run.

| Category | Commands |
| --- | --- |
| Create | `impeccable` (general design/redesign), `shape` (plan UX/UI before code, discovery interview), `craft` (deprecated alias) |
| Evaluate | `critique` (UX: hierarchy, interaction, affordance), `audit` (technical: a11y, performance, theming, quality) |
| Refine | `typeset` (typography), `layout` (spacing/rhythm), `colorize` (strategic color), `animate` (purposeful motion), `delight` (joy/personality), `bolder` (amplify), `quieter` (tone down), `overdrive` (ambitious extremes) |
| Simplify | `distill` (strip to essence), `clarify` (UX copy/microcopy), `adapt` (responsive across breakpoints) |
| Harden | `polish` (final quality pass: alignment/spacing/consistency), `optimize` (performance), `harden` (production-ready: errors, i18n, overflow), `onboard` (onboarding/first-run/empty states) |
| System | `init` (discovery interview → PRODUCT.md), `document` (scan → DESIGN.md), `extract` (pull tokens/components into design system), `live` (interactive browser variant mode) |

Working rules:

- **Match the command to the ask.** "Make the pricing page quieter" → `quieter` + a
  light detector pass (scope `layout`/`type`). "Final pass before we ship" →
  `polish` + full detector. "Redesign our landing page" → `shape` (plan) then
  `impeccable` (build), never straight to code.
- **Context before generating.** Read the client's design context (see pillar 2)
  before any design intervention. Without context, output defaults to generic
  SaaS patterns — that is exactly what the detector punishes.
- **Run the detector after every edit pass**, then fix, then re-run. See pillar 3.

#### Named design commands in Messages (P1 slash surface)

PiB Messages ships 11 of these commands as first-class slash commands that
route through the same discipline. Users type `/polish the pricing page` or
`/quieter the dashboard`, and the agent runs the discipline with the right
detector scope, resolving + citing the client Design Context (T3) and running
the T1 detector BEFORE and AFTER. A palette action menu next to the composer is
the mobile fallback for the same commands.

| Command | Scope | Discipline |
| --- | --- | --- |
| `/polish` | all | Final quality pass: alignment, spacing, consistency, contrast, edge details |
| `/typeset` | type | Typography: hierarchy, sizes, line-height, letter-spacing, measure |
| `/layout` | layout | Spacing/rhythm: padding, grid, whitespace, surface structure |
| `/colorize` | all | Strategic color: palette adherence, contrast, gradients |
| `/bolder` | type | Amplify: stronger hierarchy, contrast, presence |
| `/quieter` | layout | Tone down: less noise, more whitespace, calmer surfaces |
| `/distill` | layout | Strip to essence: remove what does not serve the primary job |
| `/clarify` | type | Copy/microcopy: clear headings, labels, CTAs, empty states |
| `/harden` | all | Production-readiness: error states, overflow, edge cases, a11y |
| `/audit` | all | Technical audit: run the full detector and fix by severity |
| `/critique` | all | UX critique: hierarchy, interaction, affordance, flow |

Non-negotiable for every named command: (1) resolve the client Design Context
(T3) — if none exists, say so and flag that an `init`/questionnaire or style
scan is needed; (2) run the T1 detector before, record the baseline; (3) apply
the discipline; (4) re-run the detector after and fix every error/warning
finding (or record a real waiver); (5) report before/after counts.

### 2. Per-client design context (PRODUCT.md/DESIGN.md equivalent)

Impeccable's durable context = `PRODUCT.md` (platform, users, positioning,
evidence, voice, anti-references) + `DESIGN.md` (colors, type, components,
radii, rules, in Google Stitch format) + per-surface briefs. PiB keeps the
same content in the Cowork wiki per client.

**Location convention** (Layer 1, zero schema changes):

- `agents/partners/wiki/design-context/<client-slug>/product.md` — the PRODUCT.md equivalent
- `agents/partners/wiki/design-context/<client-slug>/design.md` — the DESIGN.md equivalent
- `agents/partners/wiki/design-context/<client-slug>/surfaces.md` — per-surface mode briefs (optional)
- Or the same content as a Research item / client document when the client
  workstream requires it (research kind `design-context`).

**When no context exists yet, create it first:**

1. `init`-equivalent: run the discovery interview (audience, users, positioning,
   evidence, voice, anti-references) — gather from the client brief, CRM notes,
   existing site, or the user directly.
2. `document`-equivalent: scan the live site or existing repo and extract palette,
   type stack, component patterns, radii, elevation (from CSS/computed styles).
3. Write `product.md` + `design.md` into the wiki path above (template:
   `templates/design-context.md` in this skill).
4. Record it in `agents/partners/wiki/index.md` so other agents find it.

**Usage rule:** every web/design/SEO task for a client MUST read the client's
design context before generating, and MUST reference it in the task evidence.
If the context file is missing, say so and create it (or ask for the input the
interview needs) — do not silently fall back to generic SaaS defaults.

**Surface modes** (from the research): a landing page **persuades**, a dashboard
**operates**, docs **read**, a portfolio **experiences**. Tag the surface with its
mode in the task/evidence and let it change what the design must accomplish.

### 3. The detector as a runnable check

The deterministic anti-slop detector (59-60 rules: AI-slop tells + WCAG
contrast + quality basics) runs via the CLI with JSON output and exit codes.

```bash
# File/dir scan (static HTML/CSS, or regex on CSS/JSX/TSX)
npx -y impeccable detect <path> --json

# URL scan (Puppeteer full render; needs the URL reachable)
npx -y impeccable detect https://example.com --json

# Scope to a design domain (comma-separated): type, layout, ...
npx -y impeccable detect <path> --json --scope type,layout

# Mobile-width pass
npx -y impeccable detect <url> --json --viewport 390x844
```

**Exit codes:**

| Code | Meaning |
| --- | --- |
| 0 | Clean — no failing findings |
| 2 | Findings found — fix them before shipping |
| 1 | Scan error (bad path/URL, crash) |

**JSON output:** array of findings, each with `antipattern`, `name`,
`description`, `severity` (`warning`/`error`), `category` (`slop`/`quality`/...),
`file`, `line`, `snippet`. Advisory findings (e.g. em-dash overuse) appear in a
separate section and never change the exit code (`--no-advisory` hides them).

**Discipline gate — the minimum bar for every web task:**

1. Run the detector on the surface (file, dir, or live URL).
2. If exit code 2: fix every `error` and `warning` finding unless there is a
   real, stated reason (record the waiver inline: `<!-- impeccable-disable
   <rule> -- reason -->` or in the task evidence).
3. Re-run until exit 0 (or only waived/advisory findings remain).
4. Report the final exit code + finding count in the task evidence. Never claim
   a design pass without showing the detector result.

**Project config & ignores** (mirror upstream): `.impeccable/config.json`
supports `detector.ignoreRules`, `detector.ignoreFiles`,
`detector.ignoreValues`, `detector.designSystem.enabled`. Inline comments:
`impeccable-disable` (whole file), `impeccable-disable-line`,
`impeccable-disable-next-line`. `--no-config` skips project config;
`--no-design-system` skips DESIGN.md context.

**Design-system drift rules** unlock when a local `DESIGN.md` /
`.impeccable/design.json` exists — that is why pillar 2 context files should be
written into the repo/site being worked on when possible (Layer 2+ territory).

## The discipline in a PiB agent workflow

1. **Read context** — client design context (pillar 2). If missing, create it.
2. **Pick the command** — map the user ask to the vocabulary (pillar 1).
3. **Do the work** — with the mode/context framing.
4. **Detect** — run the detector (pillar 3).
5. **Fix** — iterate on findings, re-run to exit 0.
6. **Evidence** — record the command used, context read, detector exit code +
   finding count in the task output. Attach screenshots where relevant.
7. **Finish gate** — for significant design work, a fresh reviewer (never the
   builder) checks the surface against the brief contract before done
   (project pillar: "Fresh-reviewer finish gate").

## "Audit our page/site" — the Messages action card flow (T2)

When a user asks to audit a live page/site, do not just print findings in
chat. Use the PiB Design Audit action card:

1. **Open the live URL in the browser** (browser-agent/workbench tools) so the
   page actually renders and computed styles exist — or use the workbench
   `extract` control to pull outerHTML + computed styles + console errors.
   Server-side fetch (`POST /api/v1/design-audit/runs`) is the fallback for
   public URLs.
2. **Run the T1 engine** with the fetched/extracted DOM (scope `all` default,
   or `type`/`layout` narrowing). Keep it tenant-safe: the API resolves orgId
   from the authenticated user + X-Org-Id, never from an unauthenticated body.
   URL guard: http/https only, no embedded credentials, private-network
   rejection (allowPrivateNetwork opt-in), optional host allowlist.
3. **Return the design_audit rich part** — findings grouped P0-P3 with element
   refs, severity metrics (P0..P3 counts, exit code), screenshot overlay when a
   screenshot exists, evidence, and the `open_context` ref so the run opens in
   the Context Dock (`design` canvas kind). The action card arrives in
   Messages with uiActions: **Fix it** (agent edits and re-verifies),
   **Ignore + reason** (records a waiver), **Re-run**.
4. **Fix it** → make the edits, re-run the audit, and only report done when the
   re-run is clean (or every remaining finding has a real waiver).
5. **Ignore + reason** → records a waiver on the run (`POST
   /api/v1/design-audit/runs/:runId/waivers`) so the decision is auditable and
   re-runs do not re-flag it.
6. **Evidence** — task output should cite the run id, URL, scope, exit code,
   before/after finding counts, and waivers.

## Security & boundaries

- **Zero platform changes in Layer 1.** This skill only changes agent behavior.
  Do NOT add PiB API routes, schemas, or UI for the Impeccable features in this
  task — those are separate workstreams (detector engine, audit card, live
  iteration, etc.) on the same project.
- The CLI is Apache 2.0; keep attribution when embedding its rule set in
  platform code (Layer 2+).
- URL scans open a live page via Puppeteer — use only URLs the user asked to
  audit, respect private-network guards, and never scan internal/admin URLs
  that would leak data into output.
- Never fabricate detector output. If the CLI is unavailable or the scan fails,
  report the blocker; do not invent findings.

## Verification

- `npx -y impeccable --version` → 3.5.0+ (Node 22.12+ required)
- Detector smoke test: run on a sample page; expect exit 0 on clean, exit 2 on
  slop. JSON array output with `antipattern` fields.
- Context smoke test: `agents/partners/wiki/design-context/<client-slug>/product.md`
  and `design.md` exist and are referenced in the task.
