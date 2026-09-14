---
name: geo-seo-service
description: Partners in Biz GEO SEO service wrapper. Use when planning, selling, auditing, or operating GEO/AI-search visibility for PiB clients using the upstream geo-seo-claude skill bundle.
---

# GEO SEO Service — Partners in Biz

Use this skill when Peet or a PiB task mentions GEO SEO, Generative Engine Optimization, AI search visibility, AI Overviews, ChatGPT/Perplexity/Gemini visibility, llms.txt, AI crawler access, AI citability, or converting the upstream `geo-seo-claude` bundle into PiB client workflows.

## Source skill bundle

Upstream repository: `https://github.com/zubair-trabzada/geo-seo-claude`

The upstream bundle contains:
- `geo` umbrella skill
- `geo-audit`
- `geo-citability`
- `geo-crawlers`
- `geo-llmstxt`
- `geo-brand-mentions`
- `geo-platform-optimizer`
- `geo-schema`
- `geo-technical`
- `geo-content`
- `geo-report`
- `geo-report-pdf`
- `geo-prospect`
- `geo-proposal`
- `geo-compare`
- `geo-update`
- five specialist subagent prompts: AI visibility, platform analysis, technical, content, schema
- scripts for page fetch, citability scoring, brand scanning, llms.txt generation, CRM dashboard, and PDF reporting

## PiB product decision

Build GEO SEO as a separate first-class PiB module/service, not as a subsection inside the existing SEO Sprint Manager.

Recommended positioning:
- SEO Sprint Manager: traditional organic search operating system; ranks, impressions, clicks, content footprint, technical health, backlinks.
- GEO SEO Manager: AI search visibility operating system; AI understanding, trust, citation readiness, answer-engine mentions, llms.txt, AI crawler access, entity clarity, AI-friendly schema and content.
- Combined Growth Search: optional package that sells SEO + GEO together while keeping the modules distinct.

## Architecture principle

Separate service, shared plumbing.

GEO SEO should own its own:
- workspace
- audit records
- GEO score history
- findings
- tasks
- client report artifacts
- monthly comparison reports
- client portal surface

GEO SEO should reuse:
- org/client tenant scoping
- Projects/Kanban task bus
- Client Documents for proposals/reports/specs
- page fetch/crawler/schema tooling where already present
- existing SEO Sprint task creation only when a GEO finding requires traditional SEO execution

## Ownership and handoff

SEO ownership for v1 remains Sage/SEO specialist. Maya can write positioning, service packaging, client copy, and document drafts. Theo should implement platform code. Pip should create approval gates and route subtasks. Do not let Maya implement production code unless Pip explicitly routes the engineering work and the runtime policy allows it.

## Suggested PiB module shape

Admin routes:
- `/portal/geo-seo`
- `/admin/org/[slug]/geo-seo`
- `/portal/geo-seo/workspaces/[id]`
- `/portal/geo-seo/audits/[id]`
- `/portal/geo-seo/reports/[id]`

Client portal routes:
- `/portal/geo-seo`
- `/geo-report/[token]`

API namespace:
- `/api/v1/geo-seo/workspaces`
- `/api/v1/geo-seo/audits`
- `/api/v1/geo-seo/tasks`
- `/api/v1/geo-seo/reports`
- `/api/v1/geo-seo/tools`

## Data objects

`geo_workspaces`:
- `id`, `orgId`, `clientOrgId`, `siteUrl`, `siteName`
- `status`: active, paused, archived
- `mode`: audit_only, foundation_sprint, monitoring
- `currentGeoScore`, `previousGeoScore`, `lastAuditAt`, `nextAuditAt`
- optional `linkedSeoSprintId`

`geo_audits`:
- `id`, `workspaceId`, `orgId`, `siteUrl`, `auditType`
- `compositeScore`
- `categoryScores`: citability, brandAuthority, contentEEAT, technical, schema, platformReadiness
- `findings`: severity, category, title, evidence, recommendation
- optional `generatedReportDocId`, `shareToken`, `rawArtifactRefs`

`geo_tasks`:
- `id`, `workspaceId`, `orgId`, `category`, `title`, `description`
- `status`, `priority`, `sourceAuditId`
- optional `linkedSeoTaskId`, `agentProjectTaskId`, `evidence`

`geo_reports`:
- `id`, `workspaceId`, `orgId`, `auditId`, `type`, `title`, `content/artifactUrl`, `shareToken`, `status`

## SEO bridge rule

Use this ownership rule for overlapping work:
- If success is rankings, impressions, clicks, keyword movement, or organic traffic, SEO owns it.
- If success is AI understanding, citation, recommendations, brand/entity visibility, llms.txt, or AI crawler access, GEO owns it.
- If both are true, GEO owns the insight and creates linked SEO Sprint tasks for execution.

Examples:
- AI crawler access and `llms.txt`: GEO-owned.
- Entity schema for AI understanding: GEO-owned, optionally mirrored to SEO if rich results are affected.
- Technical crawlability/Core Web Vitals: SEO execution task can be linked from the GEO audit.
- Answerable content rewrites: GEO-owned unless explicitly keyword-targeted, then linked to SEO content.
- Third-party brand mentions on Reddit/YouTube/Wikipedia/directories: GEO-owned, separate from backlink pipeline.

## Recommended client packages

1. GEO Quick Audit
   - one URL/site snapshot
   - GEO score
   - crawler/llms/schema/citability quick checks
   - top 10 action list

2. GEO Foundation Sprint
   - 30-day implementation sprint
   - full audit
   - entity/schema fixes
   - llms.txt
   - answer-ready page rewrites
   - citation/mention targets
   - client report

3. GEO Monitoring Retainer
   - monthly re-audit
   - GEO score delta
   - AI platform visibility checks
   - brand mention tracking
   - new tasks/recommendations

4. Combined Growth Search
   - SEO Sprint + GEO SEO together
   - distinct ledgers, shared reporting roll-up

## Implementation phases

Phase 0 — discovery/spec:
- create an internal Client Document/spec for GEO SEO
- approve product shape and MVP scope
- create Theo/Sage/Maya tasks from the approved spec

Phase 1 — manual-service MVP:
- keep platform changes light
- use upstream GEO skill bundle manually to generate audit artifacts
- store reports as Client Documents and project docs
- create Projects tasks for execution

Phase 2 — platform MVP:
- add `geo-seo` API namespace and workspace/audit/task/report records
- add admin views and client portal read-only view
- integrate report generation with Client Documents

Phase 3 — automation:
- scheduled monthly comparisons
- AI crawler/llms/schema checks
- brand mention monitoring
- SEO Sprint bridge task generation

## Quality gates

Before giving a GEO recommendation to a client:
- verify robots.txt and AI crawler access
- verify sitemap/page discovery
- verify schema output is valid JSON-LD
- include evidence URLs/snippets for findings
- distinguish GEO-only tasks from SEO-overlap tasks
- never publish or email client-visible reports without approval

## Task closure artifacts

When completing a PiB task about GEO service strategy, return:
- the project doc URL or client document admin URL
- the wiki note path
- the repo skill path/commit if a skill wrapper was added
- a direct recommendation on separate module vs SEO Sprint integration
