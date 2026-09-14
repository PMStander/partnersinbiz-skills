---
name: seo-sprint-manager
description: >
  Manage 90-day SEO sprints for any client through the Partners in Biz platform API.
  Run daily SEO work, track keywords + rankings, manage backlinks, generate audits, and
  drive an autoresearch-style optimization loop that adapts when the plan isn't working.
  Use this skill whenever the user mentions anything SEO-related, including but not limited to:
  "do today's SEO", "run today's SEO", "do this week's SEO", "work the SEO sprint",
  "what's due in the SEO sprint", "today's SEO plan", "kick off SEO sprint",
  "create SEO sprint", "new SEO sprint", "start a 90 day SEO sprint",
  "connect search console", "GSC", "google search console", "bing webmaster tools",
  "page speed", "core web vitals", "CWV", "robots.txt check", "sitemap check",
  "metadata check", "title tag", "meta description", "canonical check", "schema validate",
  "JSON-LD", "structured data", "internal links", "internal link audit", "orphan pages",
  "keyword research", "keyword discovery", "find keywords", "winnable keywords",
  "keyword density", "track keyword", "add keyword", "retire keyword",
  "find backlinks", "discover backlinks", "directory submission", "backlink to mark live",
  "guest post pitch", "indiehackers", "saashub", "G2 listing", "Capterra",
  "publish blog post", "draft blog post", "repurpose post", "comparison page", "pillar post",
  "content cluster", "publish to insights", "schedule audit", "day 30 audit", "day 90 audit",
  "audit snapshot", "audit report", "share audit",
  "optimize sprint", "find stuck pages", "stuck pages", "approve optimization",
  "Karpathy autoresearch", "page rewrite", "lost keyword", "unindexed page",
  "what's not ranking", "why is my page not ranking", "SEO health", "sprint health",
  "compounding mode", "phase 4", "compounding SEO",
  "SEO ROI", "project organic value", "domain rating", "DR check", "OpenPageRank",
  "common crawl", "crawler simulator", "googlebot view".
  If in doubt, trigger — this skill owns the SEO sprint lifecycle from creation to
  Day 90 audit and beyond into Phase 4 (Compounding).
---

# SEO Sprint Manager — Partners in Biz Platform API

Drive 90-day SEO sprints for any client site, with three loops:

- **Loop A (Daily)** — pulls Google Search Console + Bing Webmaster Tools + PageSpeed,
  refreshes today's plan, computes sprint phase. Runs at 06:00 SAST via cron.
- **Loop B (Execution)** — when Peet says "do today's SEO", walks today's plan,
  auto-executes safe tasks, queues anything that publishes for human review.
- **Loop C (Optimization — Karpathy autoresearch)** — weekly cron + on-demand. Detects
  health signals (stuck pages, lost keywords, zero-impression posts, etc.), proposes
  hypotheses, generates new tasks, measures outcomes 14 days later, scores wins/losses.

After Day 90, sprints transition to **Phase 4 (Compounding)** — Loop A still runs daily,
Loop C generates work weekly. The sprint never "ends" until archived.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## UI surfaces

| Audience | URL | What's there |
|---|---|---|
| Admin (operator mode) | `/portal/seo` | Index of all sprints across all clients + presence pill + "+ New Sprint" |
| Admin (workspace mode) | `/admin/org/[slug]/seo` | Per-client SEO landing — redirects to the active sprint cockpit, or shows "+ Create sprint" CTA if none exists. Also rendered in the sidebar as a collapsible **SEO Sprint** section with links to all 9 cockpit tabs. |
| Admin sprint cockpit | `/portal/seo/sprints/[id]` | Today / Tasks / Keywords / Backlinks / Content / Audits / Optimizations / Health / Settings |
| Admin tools (standalone) | `/portal/seo/tools` | Run any of the 13 in-house SEO tools by hand |
| Client portal | `/portal/seo` | Hero dashboard for single-sprint clients (day-of-90, progress, top movers, recent wins, deep links). Multi-sprint clients see a card list. |
| Public audit share | `/seo-audit/[token]` | Read-only audit snapshot the admin can hand to a client |

When creating a sprint via the UI in workspace mode, the form pre-fills `orgId`/`clientId` from the URL query params (`?orgId=X&siteName=Y`) which the per-org page passes through. When in operator mode the user picks the org from a dropdown.

## Non-negotiable operating rule: the sprint is the client-visible ledger

Any SEO work done for a client must end in the Partners in Biz SEO sprint, not only in
the client's app repo, GitHub PR, or wiki. The website/code PR is the implementation
record, the wiki is the internal knowledge record, and the SEO sprint is the
client-facing progress record. This applies equally when a client-specific agent is
working in another app repository and only uses Partners in Biz as the growth
platform.

For every SEO pass:

1. Resolve the client org id and active SEO sprint.
2. Read today's plan and overdue tasks before choosing work.
3. Match the work performed to existing sprint tasks where possible.
4. Mark completed sprint tasks done with notes/evidence:
   - GitHub PR/commit links
   - build/check evidence
   - audit/artifact references
   - exact findings or before/after notes
5. Move partly handled tasks to `in_progress` with the remaining work described.
6. Move blocked tasks to `blocked` with a concrete blocker reason.
7. Add an audit, artifact, content row, optimization, keyword, or backlink row when the work produced one.
8. Finish with a digest that includes sprint task ids/statuses, blockers, and any human tickets created.

Do not report "SEO done" if the client-visible sprint still shows the work as due.

When an SEO task is blocked, the blocker reason must be detailed enough for an
admin or client to act. Include:

- what is wrong
- how to fix it
- what proof is needed
- the exact instruction to send the agent after the blocker is resolved

The platform creates/reuses the client SEO project, creates a blocker task, and
notifies matching admins when an SEO task is marked `blocked`. Agents should still
make the blocker reason useful; the platform cannot infer missing context.

## Human blockers and cross-app handoff

When a task needs Peet, a Partners in Biz team member, or the client to do something
the agent cannot do, create a Partners in Biz project ticket instead of leaving the
request only in chat or a wiki note.

Canonical flow:

1. Look for an active client project for the workstream, for example
   `AHS Law - SEO 90-day Sprint`.
2. If no suitable project exists, create one with `POST /projects`:
   - `orgId`: the client's org id
   - `clientId` / `clientOrgId`: the same client org id unless a separate billing org is known
   - `name`: `<Client> - SEO 90-day Sprint`
   - `status`: `development` while work is actively being executed, or `discovery` during setup
   - `brief`: include the sprint id, site URL, goals, and the rule that this project tracks human/agent work related to the SEO sprint.
3. Create a project-nested task with `POST /projects/{projectId}/tasks`.
4. Label the task so it remains tied to the module:
   - `seo`
   - `seo-sprint:<sprintId>`
   - `client-action`, `peet-action`, or `team-action`
   - `blocked` when it blocks sprint progress
5. Link the task back from the SEO sprint task by adding the project/task URL or id to
   the SEO task description or blocker reason.
6. If the exact human user id is known, assign or mention them (`assigneeIds` /
   `mentionIds`). If not, leave it unassigned but make ownership explicit in the
   title, for example `Client action: confirm public business address`, and add the
   `needs-assignment` label.
7. Do not mark the SEO task done until the human blocker is resolved and proof is
   recorded in the sprint.

Use this pattern across app workstreams too: the domain-specific module records its
own progress, while the Projects task carries cross-team execution, ownership,
mentions, dependencies, and agent handoff.

## Auth

```
Authorization: Bearer ${AI_API_KEY}
```

Prefer the user-delegation Bearer token (`pib_dlg_…`) or a device-login / personal token from `pib-skills login` (see `system-auth`). `AI_API_KEY` is for cron/system jobs only. On 403, print the API error and stop — do not retry with a god-key. The `AI_API_KEY` env var is set on Vercel for `partnersinbiz-web` for cron/system jobs; it auths as role `ai` which gets admin-equivalent access.

## orgId / clientId rules

Both `orgId` and `clientId` on a sprint **must equal the Firestore `organizations` document id** (e.g. `pib-platform-owner`, `gqkkZPlHEPLbrSPuYjlp` for AHS Law) — not the slug, not the org name. The sidebar lookup, portal scoping, and the `requireSprintAccess` tenant check all key off this.

To resolve an org id from a slug or name:
```bash
curl -s "https://partnersinbiz.online/api/v1/organizations" \
  -H "Authorization: Bearer $AI_API_KEY" \
  | jq -r '.data[] | "\(.id)\t\(.slug)\t\(.name)"'
```

Behaviour of the create endpoint by role:

- **`ai` / `admin`**: `body.orgId` (or `body.clientId`) is honoured so a sprint can be scoped to any client. Falls back to `user.orgId` only if neither is sent.
- **`client`**: locked to `user.orgId` — they cannot create sprints for other orgs.

## Base URL

```
https://partnersinbiz.online/api/v1/seo
```

Override via `PIB_API_BASE` for local dev.

## The "Do today's SEO" flow

```
GET  /seo/sprints?status=active                      # find active sprints
GET  /seo/sprints/[id]/today                         # what's due today
POST /seo/sprints/[id]/run                           # execute Loop B end-to-end
```

`/run` returns `{ done: [taskIds], queued: [taskIds], blocked: [{taskId, reason}], agentHandoff? }`.

When `/run` queues work for Hermes, the platform creates or updates a watcher-visible
project task assigned to Pip:

- `assigneeAgentId: "pip"`
- `agentStatus: "pending"`
- `agentEffort: "high"` for orchestration/research-heavy runs unless the work is routine
- `source: "seo-run-orchestration"`
- `agentInput.context.orchestrationMode: "pip-orchestrator"`
- `agentInput.context.queuedSeoTaskIds: [...]`

That project task is what the VPS `agent-watcher` dispatches to Hermes. Do not treat
`queued` as dispatched unless the response has `agentHandoff` or the relevant
`seo_tasks` have `agentProjectTaskId`.

The watcher now injects project context and dependency summaries into dispatch
prompts, but SEO orchestration tasks should still keep `agentInput.context`
specific enough to map the wrapper task back to the source `seo_tasks`.

### Closing SEO handoff project tasks

When Hermes/Pip receives a `seo-run-orchestration` project task, the project task is
only the orchestration wrapper. The source of truth is still the SEO sprint ledger.
Before marking the project task `agentStatus: done`, always sync the wrapper back to
the child `seo_tasks`:

1. Re-read every id in `agentInput.context.queuedSeoTaskIds` or `sourceSeoTaskIds`.
2. Set each checklist item done only when the matching `seo_tasks/{id}.status` is `done`.
3. Leave blocked SEO tasks as unchecked and make sure each has a concrete `blockerReason`.
4. If all reachable work is complete and only blocker tickets remain, move the wrapper
   project task to `columnId: done` and set `agentStatus: done`.
5. If the agent itself is blocked and cannot complete the orchestration, set
   `columnId: blocked`, `agentStatus: blocked`, and write the exact recovery action.
6. Never leave a project task with `agentStatus: done` in an active kanban column, and
   never report "SEO done" when its checklist still shows unfinished child SEO tasks
   without explaining that they are blockers or pending release.

Pip's natural-language flow when Peet says "do today's SEO":

1. Find active sprints (filter by client if mentioned)
2. For each, GET today's plan
3. POST /run to execute autopilot tasks + queue the rest
4. If `agentHandoff` is present, include the project/task id so the user can see the Hermes handoff.
5. Report a short digest: "Did 4, queued 2 to Pip/Hermes, 1 blocked on GSC reconnect"

## Endpoints

### Sprints
```
GET    /seo/sprints                                  list (filter: status, clientId)
POST   /seo/sprints                                  create from outrank-90 template
GET    /seo/sprints/[id]                             single sprint
PATCH  /seo/sprints/[id]                             update (autopilot mode, etc)
POST   /seo/sprints/[id]/archive                     soft-archive (force=true to delete)
GET    /seo/sprints/[id]/today                       today's plan
GET    /seo/sprints/[id]/health                      health + integration status
POST   /seo/sprints/[id]/optimize                    trigger Loop C on demand
POST   /seo/sprints/[id]/run                         trigger Loop B (do today's SEO)
```

### Tasks
```
GET    /seo/sprints/[id]/tasks                       list (filters: week, phase, status, source, taskType)
POST   /seo/sprints/[id]/tasks                       add custom task
PATCH  /seo/tasks/[id]                               update
POST   /seo/tasks/[id]/complete                      mark done
POST   /seo/tasks/[id]/skip                          mark skipped
POST   /seo/tasks/[id]/execute                       run executor for a single task
```

### Keywords
```
GET    /seo/sprints/[id]/keywords                    list
POST   /seo/sprints/[id]/keywords                    add (or POST?bulk=true with {keywords: [...]})
PATCH  /seo/keywords/[id]                            update
DELETE /seo/keywords/[id]                            soft-delete
POST   /seo/keywords/[id]/retire                     mark lost
GET    /seo/keywords/[id]/positions                  full time series
```

### Backlinks
```
GET    /seo/sprints/[id]/backlinks                   list
POST   /seo/sprints/[id]/backlinks                   add manually
PATCH  /seo/backlinks/[id]                           update
POST   /seo/backlinks/[id]/mark-live                 transition to live
GET    /seo/sprints/[id]/backlinks/discover          run Bing WMT + Common Crawl discovery
```

### Content
```
GET    /seo/sprints/[id]/content                     list
POST   /seo/sprints/[id]/content                     add idea
PATCH  /seo/content/[id]                             update
POST   /seo/content/[id]/draft                       AI-draft the post
POST   /seo/content/[id]/repurpose                   handoff to social-media-manager
POST   /seo/content/[id]/publish                     mark live + persist `slug` → auto-publishes to /insights/[slug]
POST   /seo/content/[id]/client-approve              client approval for reviewed SEO/content item
DELETE /seo/content/[id]/comments/[commentId]        remove a content comment
```

### Audits
```
GET    /seo/sprints/[id]/audits                      list
POST   /seo/sprints/[id]/audits                      generate snapshot now
GET    /seo/audits/[id]                              audit detail
GET    /seo/audits/[id]/share                        get/create public share token
GET    /seo/audits/[id]/report.pdf                   PDF (501 — coming soon)
```

### Optimizations (Karpathy autoresearch log)
```
GET    /seo/sprints/[id]/optimizations               list (filter: status, result)
POST   /seo/optimizations/[id]/approve               turn proposal → tasks
POST   /seo/optimizations/[id]/reject
POST   /seo/optimizations/[id]/measure               re-measure outcome (win/loss/no-change)
```

`POST /seo/sprints/[id]/optimize` returns `{ signalsFound, proposalsCreated, agentHandoff? }`.
When proposals are created, the platform creates or updates a watcher-visible project
task assigned to Pip:

- `assigneeAgentId: "pip"`
- `agentStatus: "pending"`
- `source: "seo-optimization-orchestration"`
- `agentInput.context.orchestrationMode: "pip-orchestrator"`
- `agentInput.context.optimizationIds: [...]`

Hermes/Pip should review each proposal, approve useful proposals via
`POST /seo/optimizations/[id]/approve`, run the generated tasks where appropriate,
reject weak/duplicate proposals, and report optimization ids, generated task ids,
completed task ids, blockers, and evidence.

When closing a `seo-optimization-orchestration` project task, apply the same wrapper
rule: re-read every `optimizationId`, update the project checklist from the actual
optimization/task outcomes, move the wrapper to Done only when the orchestration work
is finished, and keep unresolved human/client/admin actions as separate blocker or
review tasks.

### In-house SEO toolkit
```
POST   /seo/tools/metadata-check                     {url} → title/meta/og audit
POST   /seo/tools/robots-check                       {domain}
POST   /seo/tools/sitemap-check                      {sitemapUrl}
POST   /seo/tools/canonical-check                    {url}
POST   /seo/tools/crawler-sim                        {url} → render as Googlebot
POST   /seo/tools/schema-validate                    {url} → JSON-LD validation
POST   /seo/tools/title-generate                     {topic, keyword} → 5 candidates
POST   /seo/tools/meta-generate                      {topic, keyword} → 3 candidates
POST   /seo/tools/slug-generate                      {title} → URL slug
POST   /seo/tools/keyword-density                    {url, keyword}
POST   /seo/tools/keyword-discover                   {seedKeywords[], siteUrl}
POST   /seo/tools/internal-link-audit                {sitemapUrl}
POST   /seo/tools/seo-roi                            {keywords[], conversionRate, avgValue}
POST   /seo/tools/page-fetch                         {url} → cached fetch
```

### Integrations
```
GET    /seo/integrations/gsc/auth-url?sprintId=X     start OAuth flow
GET    /seo/integrations/gsc/callback                OAuth callback (redirect target)
POST   /seo/integrations/gsc/connect/[sprintId]      pick GSC property
POST   /seo/integrations/gsc/disconnect/[sprintId]
POST   /seo/integrations/gsc/pull/[sprintId]         on-demand pull
GET    /seo/integrations/gsc/properties/[sprintId]   list GSC properties for connected account
POST   /seo/integrations/gsc/sitemaps/submit/[sprintId] submit sitemap.xml or {sitemapUrl}
POST   /seo/integrations/bing/connect/[sprintId]     {siteUrl}
POST   /seo/integrations/pagespeed/run/[sprintId]    on-demand pull
```

### GSC API capability map

Agents must be precise about what the connected Google Search Console API can and
cannot do.

**Current OAuth scope**

PiB requests `https://www.googleapis.com/auth/webmasters`, not readonly. This is the
Search Console read/write scope and is needed for sitemap submission. Existing
connections made before this scope change may only have
`https://www.googleapis.com/auth/webmasters.readonly`; if sitemap submit returns an
insufficient-scope error, reconnect GSC from the sprint Settings tab, select the
property again, then retry.

**Can do through the PiB API**

- List verified GSC properties:
  `GET /seo/integrations/gsc/properties/[sprintId]`.
- Select the property used by the sprint:
  `POST /seo/integrations/gsc/connect/[sprintId]` with `{ "propertyUrl": "sc-domain:example.com" }`.
- Pull Search Analytics data for keyword/page tracking:
  `POST /seo/integrations/gsc/pull/[sprintId]`.
- Inspect known URL status from Search Console through executors/tools that call
  Google's URL Inspection API. This reads Google's URL-level state; it does not
  request indexing.
- Submit a sitemap:
  `POST /seo/integrations/gsc/sitemaps/submit/[sprintId]`.
  Body is optional; omit it to submit `${siteUrl}/sitemap.xml`, or send
  `{ "sitemapUrl": "https://example.com/sitemap.xml" }`.

**Cannot do through any normal GSC API**

- The Search Console UI's **Request indexing** action for ordinary pages is not
  exposed as a Search Console API method. Keep `gsc-request-index` tasks manual:
  a verified user must open URL Inspection in the Search Console UI, inspect the
  page, and click Request indexing.
- Google's separate Indexing API is not a general replacement. It is only for
  pages with `JobPosting` structured data or livestream `BroadcastEvent` content
  embedded in `VideoObject`. Do not use it for standard Partners/client landing,
  service, blog, or pricing pages.

When closing SEO blockers, mark sitemap submission as agent-actionable if the sprint
has a write-scoped GSC token and selected property. Keep URL Inspection request
indexing as a human/client action unless the page is genuinely eligible for Google's
special Indexing API.

## Examples

### Create a sprint for a client
```bash
# 1. Look up the org's Firestore id (use slug to find it)
ORG_ID=$(curl -s "$BASE/../organizations" \
  -H "Authorization: Bearer $AI_API_KEY" \
  | jq -r '.data[] | select(.slug=="ahs-law") | .id')

# 2. Create the sprint — pass orgId AND clientId, both = ORG_ID
# Optional: companyId (or sourceCompanyId) scopes the sprint to a CRM company.
# When that company is linked, the client org sees the sprint under Shared with us
# unless clientVisibility is set to "private".
curl -X POST $BASE/sprints \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: sprint-$(date +%s)" \
  -d "{\"orgId\":\"$ORG_ID\",\"clientId\":\"$ORG_ID\",\"siteUrl\":\"https://ahs-law.co.za\",\"siteName\":\"AHS Law\",\"companyId\":\"$COMPANY_ID\"}"
```

Returns `{ id, siteUrl, siteName, status: 'pre-launch' }`. Sprint is seeded with 42
template tasks + 15 directory backlinks (children inherit `companyId`). After creation, the sprint immediately
appears in the workspace sidebar when that client is selected, and at
`/portal/seo` for that client's portal users. Linked-org viewers open projected
sprints via `GET /api/v1/company-work/shared?module=seo`.

### Company scope + client projection

| Field | Meaning |
|---|---|
| `companyId` / `sourceCompanyId` | Stamp on create (query or body). Company view filters to that company; org view includes company rows with a badge. |
| `clientVisibility` | `shared` (default) or `private`. Private records are withheld from the linked org projection. |
| Linked-org access | `company_workspace` grant with `seo` in `items[]` → view / comment / approve via `requireSprintAccess` projection branch. |

Portal deep-links from a company workspace must keep `sourceCompanyId` on `/portal/seo?...`.

### Do today's SEO across all active sprints
```bash
# 1. List active sprints
curl "$BASE/sprints?status=active" -H "Authorization: Bearer $AI_API_KEY"

# 2. For each, run the execution loop
for id in $SPRINT_IDS; do
  curl -X POST "$BASE/sprints/$id/run" \
    -H "Authorization: Bearer $AI_API_KEY" \
    -H "Idempotency-Key: run-$id-$(date +%s)"
done
```

### Add 5 keywords in bulk
```bash
curl -X POST "$BASE/sprints/$ID/keywords?bulk=true" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"keywords":[
        {"keyword":"acme alternative","volume":1300,"intentBucket":"solution"},
        {"keyword":"how to acme","volume":2400,"intentBucket":"problem"}
      ]}'
```

### Approve all open optimizations
```bash
curl "$BASE/sprints/$ID/optimizations?status=proposed" -H "Authorization: Bearer $AI_API_KEY" \
  | jq -r '.data[].id' \
  | while read oid; do
      curl -X POST "$BASE/optimizations/$oid/approve" \
        -H "Authorization: Bearer $AI_API_KEY" \
        -H "Idempotency-Key: approve-$oid"
    done
```

### Generate Day 30 audit
```bash
curl -X POST "$BASE/sprints/$ID/audits" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"snapshotDay":30}'
```

### Submit the sprint sitemap to GSC
```bash
curl -X POST "$BASE/integrations/gsc/sitemaps/submit/$ID" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Idempotency-Key: sitemap-$ID-$(date +%s)"
```

## Cross-skill handoffs

- **`/content/[id]/repurpose`** calls `/api/v1/social/posts` (the social-media-manager
  skill's namespace) to draft LI + X posts. Records `liUrl` and `xUrl` on the
  `seo_content` doc.
- **Day 90 announcement** (week-13 task `audit-announce`) hands off to
  `social-media-manager` to schedule the audit announcement post.

## Idempotency

All POST creates and side-effect endpoints accept `Idempotency-Key` header.
Same key replays cached response within 24h.

## Audit trail

All writes include `createdBy`, `createdByType` (`user|agent|system`), `updatedBy`,
`updatedByType`. Pip's writes show as `agent` in the audit log.

## When tools error

If the cron has been failing or GSC tokens expired, sprint health will show
`integrations.gsc.tokenStatus = 'expired'`. Surface this as: "GSC connection expired
for [client] — needs reconnect at /portal/seo/sprints/[id]/settings".

## Client Document Handoff

When an SEO sprint needs client strategy sign-off, create or link a client document through the `client-documents` skill. Use a strategy/spec-style document, link it with `linked.seoSprintId`, and keep implementation work in the SEO sprint tasks.
