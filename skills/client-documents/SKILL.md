---
name: client-documents
description: Create, review, publish, and track client-facing PiB documents including proposals, specs, social strategies, content campaign plans, reports, launch sign-offs, and change requests.
---

# Client Documents

Use this whenever Peet asks for a proposal, spec, strategy document, sign-off, report, change request, approval pack, or any client-facing document.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## What This Is

`client_documents` are the collaboration and approval layer between PiB and clients. They live at:
- Admin view: `https://partnersinbiz.online/portal/documents/[id]`
- Org-scoped admin: `https://partnersinbiz.online/admin/org/[slug]/documents/[id]`
- Client portal: `https://partnersinbiz.online/portal/documents/[id]`
- Public share page: `https://partnersinbiz.online/d/[shareToken]` (only after publish)

Projects, campaigns, CRM deals, reports, SEO sprints, and social posts remain the operational source of truth. Documents are linked to them via `document.linked`.

---

## CRM Relationship Model

Document ownership, CRM-company linkage, and client organisation visibility are separate.

- `orgId` is the document source/owner workspace. **PiB-authored client work must stay owned by the platform/CRM org** (usually `pib-platform-owner` or the Partners in Biz workspace), not the client's org.
- `linked.companyId` attaches the document to a CRM company and is required for company Documents tabs.
- `linked.clientOrgId` makes a PiB-owned document visible in a system client's organisation document list **only after status is client-visible** (`client_review`, `changes_requested`, `approved`, `accepted`). Internal drafts never appear under the client org index.
- Opening a document from PiB CRM company Documents stays in the document owner org — it does **not** switch the portal into the client workspace.
- Existing documents should not be re-owned just to make them appear in another view. Link them with `linked.companyId` and, where applicable, `linked.clientOrgId`.
- PiB-prepared documents for system clients should normally be source-owned by `pib-platform-owner` and linked to the client through `linked.companyId` + `linked.clientOrgId`.
- Non-system CRM businesses have no client organisation. For them, use `linked.companyId` only; they show under the CRM company Documents tab but not in any client portal Documents tab.

When creating from a CRM company page, prefer the current page company context:

```json
{
  "title": "AHS Law — Google Ads Proposal",
  "type": "sales_proposal",
  "templateId": "sales_proposal",
  "linked": { "companyId": "<crmCompanyId>" }
}
```

The API resolves the owner org from the company. If that company has `linkedOrgId`, the API also stamps `linked.clientOrgId`, so the client organisation sees the document after publish.

When creating from a selected client/org context instead of a company page, send the client `orgId`. The API finds the PiB-side platform CRM company and stores the document under `pib-platform-owner` when that relationship exists.

Publishing / "send to client" changes the document to `client_review`, enables share, and makes it appear in client-visible document lists. Client-visible statuses are only `client_review`, `changes_requested`, `approved`, and `accepted`; `internal_draft` and `internal_review` stay hidden from clients.

After publishing a CRM-linked client document, verify it through both views:

1. CRM company Documents tab includes the document via `linked.companyId`.
2. Client/org Documents list includes it via `linked.clientOrgId` and client-visible status.

Do not rely on email notification alone as proof of client visibility; verify the document list/API.

---

## Share modes

A document supports two independent shares — view-only and edit. They are independently revocable.

### View-only share (`/d/[shareToken]`)

Public, no authentication required. Anyone with the link can see the document. Enable by publishing the document. Use for: pitch decks, signed-off proposals, final reports anyone can read.

### Edit share (`/d/[editShareToken]/edit`)

Code-gated + authenticated. Recipients must:
1. Enter the 6-character access code admin generated
2. Sign in via magic-link email OR Google OAuth
3. (Their identity is captured so every comment, suggestion, or edit is recorded against a verified email)

What they can do once authenticated is controlled by `document.clientPermissions` (comments, suggestions, direct edits, approvals — independently toggleable).

Use for: client review cycles, collaborative editing with external stakeholders, anyone whose feedback you need to attribute.

---

## Document Types & Templates

| `type` / `templateId` | Label | Approval mode | Use for |
|---|---|---|---|
| `sales_proposal` | Sales Proposal | `formal_acceptance` | New client pitches, SOW-level agreements |
| `build_spec` | Website/App Build Spec | `operational` | Web/app project scopes |
| `social_strategy` | Social Media Strategy | `operational` | Social channel + content strategies |
| `content_campaign_plan` | Content Campaign Plan | `operational` | Campaign briefs, asset plans |
| `research_report` / `research-report-v1` | Research Report | `operational` | Evidence-led research questions, source ledgers, confidence, unknowns, recommendations, and decision support |
| `monthly_report` | Monthly Report | `operational` | Monthly performance reviews |
| `launch_signoff` | Launch Sign-off | `operational` | Go-live checklists and sign-off |
| `change_request` | Change Request | `operational` | Scope/budget/timeline change requests |
| `canvas_draft` / `canvas-draft-v1` | Canvas Draft | `operational` | Internal-only staging doc auto-created when a Creative Canvas text node is published to `client_document`/`blog_post` (target of `POST /api/v1/creative-canvas/[id]/exports/draft`). Not in the public API's creatable-types allowlist — do not create these directly; they arrive via canvas publishes. |

**Approval modes:**
- `operational` — client clicks an "Approve" button (most documents)
- `formal_acceptance` — client must type their name + check a box (proposals/SOW only). Formal documents can also carry a PiB-side countersignature through `POST /api/v1/client-documents/[id]/sign` after a published version exists.

---

## Block Types

Each document version is an ordered array of `DocumentBlock` objects. Fill `content` based on block type:

| Block type | Content shape | Notes |
|---|---|---|
| `hero` | `string` (subtitle / tagline) | Always first. Title comes from `document.title`. |
| `summary` | `string` (plain prose) | Executive summary or overview. **Not Markdown** — use real newlines; put section titles in `block.title`. |
| `problem` | `string` (plain prose) | Problem statement, audience pain, context. **Not Markdown.** |
| `scope` | `string` or `string[]` (bullet list) | What is in scope |
| `deliverables` | `string[]` (list of deliverables) | Concrete outputs |
| `timeline` | `{ phases: [{ label: string, duration: string, description?: string }] }` | Milestone phases |
| `investment` | `{ items: [{ label: string, amount: number, currency?: string }], total: number, currency?: string, notes?: string }` | Pricing table |
| `terms` | `string` (plain prose) | Payment terms, IP, cancellation. **Not Markdown.** |
| `approval` | `string` (instructions text for client) | Shown above the approve button |
| `metrics` | `{ items: [{ label: string, value?: string, target?: string, description?: string }] }` | KPIs / success metrics |
| `risk` | `string[]` or `string` | Known risks, assumptions, limitations |
| `table` | `{ headers: string[], rows: string[][] }` | Generic data table |
| `gallery` | `string[]` (image URLs) | Image gallery |
| `callout` | `{ title: string, body: string, variant?: 'info'\|'warning'\|'success' }` | Highlighted callout box |
| `rich_text` | `string` (plain prose) | Free-form section. **Not Markdown** — `###` / `**` / `` ` `` render as literal characters. Prefer splitting into titled blocks + `table` / `faq` / `scope`. |
| `image` | `{ url, alt?, caption?, width?: 'normal'\|'wide'\|'full' }` | Lazy-loaded; `wide` breaks past prose column, `full` is edge-to-edge |
| `video` | `{ url, provider?: 'youtube'\|'loom'\|'vimeo'\|'mux', caption? }` | Auto-detects provider from URL; lazy iframe |
| `embed` | `{ url, height?: number, caption? }` | Sandboxed iframe; only allowed hosts (Calendly, Tally, Typeform, Figma, CodeSandbox, Google Docs/Forms) — others fall back to a plain link |
| `link_card` | `{ url, title, description?, image?, favicon? }` | OG-style card with hover lift and hostname badge |
| `chart` | `{ kind: 'bar'\|'pie'\|'line'\|'progress_ring', data, title?, options? }` | Recharts; auto-themed from accent palette |
| `pricing_toggle` | `{ items: [{label, amount, required?, default?}], currency, note? }` | Interactive — client toggles add-ons, total updates live |
| `faq` | `{ items: [{q, a}] }` | Native `<details>` accordion |
| `comparison` | `{ headers: string[], rows: [{label, values: (string\|boolean)[]}], highlightCol?: number }` | Highlight column tinted accent; boolean cells render as check/cross icons |

> ⚠️ **Prose blocks are plain text, not Markdown.** `summary`, `problem`, `terms`, `hero`, `approval`, and `rich_text` render with `whitespace-pre-wrap` only. Never put `###`, `**`, `` ` ``, or Markdown lists in content — they show literally to the client. Use `block.title` for headings and structured blocks (`table`, `scope`, `deliverables`, `faq`, `callout`, `metrics`, `timeline`, `comparison`, `risk`) for structure. Use real newlines in JSON strings (not the two-character sequence `\n`).

> ⚠️ **Theme contrast for tables:** alternating table rows use `--doc-surface`. Prefer the default dark palette (`bg` near `#0A0A0B`, light `text`, gold `accent`), or set `palette.surface` / `border` / `muted` explicitly for light themes. Light `bg` without those fields now auto-derives readable surface colors in the renderer, but older light-only palettes still looked broken (dark surface + dark text).

> ⚠️ **Match the content shape exactly — the wrong shape crashes the whole document, it does not degrade gracefully.** The renderer maps `content` straight onto React children, so handing a block an unexpected object/array throws React error #31 ("Objects are not valid as a React child") and the *entire* document page renders "Document not found" / blank for both admin and client. Most common footguns: `risk` must be `string[]` (NOT `[{severity, item}]`), `timeline` must be `{ phases: [...] }` (NOT `[{phase, detail}]`), `approval`/`terms`/`hero`/`summary`/`problem` must be plain `string` (NOT objects), `metrics` must be `{ items: [...] }` with `value`/`target` as **strings** not integers. When copying blocks from an older document version, re-validate every shape against this table — older drafts may use shapes a newer renderer rejects.

**Display motion options (optional):** `none` | `reveal` | `sticky` | `counter` | `timeline`
- Use `reveal` on most prose/list blocks (fade-and-slide on scroll into view)
- Use `counter` on `metrics` blocks (animates numeric values from 0 → target on scroll)
- Use `sticky` on `hero` for parallax effect
- Use `timeline` on `timeline` blocks for sequential phase reveal

---

## Status Flow

```
internal_draft → internal_review → client_review → changes_requested → approved → accepted
                                                                       ↑_________↓ (loop)
```
- `internal_draft` / `internal_review`: not visible to client
- `client_review`: client can see and comment (requires publish)
- `changes_requested`: client requested changes via portal
- `approved`: operational approval given
- `accepted`: formal acceptance signed by the client (proposals only); the rendered/shared copy also shows PiB countersignature evidence when `providerSignature` is present
- `archived`: soft-deleted from active views

Research reports follow the same status flow, but keep them internal unless Peet has approved client visibility and the report has passed the research checklist: source ledger is safe to expose, confidence/assumptions are explicit, sensitive internal notes are removed, recommendations do not imply unapproved spend/publishing/implementation, and the linked `research_item` visibility is appropriate.

## Document Business Insight Signals

Client documents now feed the `business-insight-review` loop. Treat these as proactive business signals, not just document statuses:

| Metric | Trigger | Agent action |
|---|---|---|
| `client_documents_waiting_for_review` | A document sits in `client_review` for 7+ days. | Check owner/client follow-up state, create internal unblock work when needed, and preserve the client-visible approval gate. |
| `client_documents_changes_requested` | A document is in `changes_requested`. | Read comments/suggestions, draft the revision plan, and link work back to the document/project. |
| `client_documents_blocking_publish_assumptions` | A document has open `blocks_publish` assumptions. | Resolve or escalate the blocker before anyone asks to publish, send, or approve the document. |

Loop-generated document insight tasks are internal by default and carry `requiredCapability: "business-insight-review"`. Do not publish, send, approve, accept, countersign, change sharing, or message the client from these tasks without explicit approval. If an approved insight should become execution work, convert it through the project task action route and keep the document linked through `linked.projectId`.

---

## Full API Reference

Base URL: `https://partnersinbiz.online`
Auth: interactive runs use the user-delegation Bearer token (`pib_dlg_…`) + `X-Org-Id: <orgId>` (see `## Auth (mandatory)` above); `Authorization: Bearer <AI_API_KEY>` + `X-Org-Id: <orgId>` is cron/system only.
All responses: `{ success: boolean, data: ... }` — always unwrap `body.data ?? body`.

### Documents

| Method | Route | Body / Params | Notes |
|---|---|---|---|
| `GET` | `/api/v1/client-documents` | `?orgId=&status=&type=&limit=&page=` | List documents |
| `POST` | `/api/v1/client-documents` | `{ orgId?, title, type, templateId?, linked? }` | Create document (starts as `internal_draft`). From CRM company context, send `linked.companyId`; the API resolves the owner org and `linked.clientOrgId` when possible. |
| `GET` | `/api/v1/client-documents/[id]` | — | Fetch single document |
| `PATCH` | `/api/v1/client-documents/[id]` | `{ title?, status?, orgId?, linked?, assumptions?, clientPermissions?, shareEnabled? }` | Update metadata |
| `DELETE` | `/api/v1/client-documents/[id]` | — | Archive (soft delete) |
| `POST` | `/api/v1/client-documents/[id]/archive` | `{}` | Explicit admin archive action; use this from admin UI/workflows when available |
| `POST` | `/api/v1/client-documents/[id]/publish` | `{}` | Move to `client_review`, generate shareToken |

### Edit share

| Method | Route | Body | Notes |
|---|---|---|---|
| `POST` | `/api/v1/client-documents/[id]/edit-share/enable` | `{}` | Generates editShareToken + 6-char editAccessCode. Sets editShareEnabled=true |
| `POST` | `/api/v1/client-documents/[id]/edit-share/regenerate-code` | `{}` | Rotates only the access code. Token preserved |
| `POST` | `/api/v1/client-documents/[id]/edit-share/disable` | `{}` | Sets editShareEnabled=false. Token + code preserved for re-enable |
| `GET` | `/api/v1/client-documents/[id]/access-log?limit=N` | — | Last N access events (code attempts + auth events). Default 20, max 100 |

### Versions

| Method | Route | Body | Notes |
|---|---|---|---|
| `GET` | `/api/v1/client-documents/[id]/versions` | — | List all versions |
| `POST` | `/api/v1/client-documents/[id]/versions` | `{ blocks, theme, changeSummary? }` | Create new draft version |
| `GET` | `/api/v1/client-documents/[id]/versions/[versionId]` | — | Fetch specific version |
| `GET` | `/api/v1/portal/documents/count` | — | Portal-visible document count for the active org |
| `GET` | `/api/v1/portal/documents/unresolved-count` | — | Portal-visible unresolved document comments/suggestions count |

### Comments

| Method | Route | Body | Notes |
|---|---|---|---|
| `GET` | `/api/v1/client-documents/[id]/comments` | `?blockId=&status=` | List comments |
| `POST` | `/api/v1/client-documents/[id]/comments` | `{ text, blockId?, anchor? }` | Add comment |
| `PATCH` | `/api/v1/client-documents/[id]/comments/[commentId]` | `{ status }` | Resolve comment |
| `POST` | `/api/v1/client-documents/[id]/comments/[commentId]/replies` | `{ text }` | Add a threaded reply |
| `POST` | `/api/v1/client-documents/[id]/comments/[commentId]/resolve` | `{}` | Mark a comment resolved |

### Suggestions

| Method | Route | Body | Notes |
|---|---|---|---|
| `GET` | `/api/v1/client-documents/[id]/suggestions` | `?blockId=&status=` | List suggestions |
| `POST` | `/api/v1/client-documents/[id]/suggestions` | `{ blockId?, versionId?, originalText?, suggestedText, reason? }` | Add a client/editor suggestion |
| `POST` | `/api/v1/client-documents/[id]/suggestions/[suggestionId]/accept` | `{}` | Accept a client suggestion |
| `POST` | `/api/v1/client-documents/[id]/suggestions/[suggestionId]/reject` | `{}` | Reject a suggestion |

### Approvals

| Method | Route | Body | Notes |
|---|---|---|---|
| `POST` | `/api/v1/client-documents/[id]/approve` | `{ actorName, mode }` | Operational approval (agent/admin) |
| `POST` | `/api/v1/client-documents/[id]/accept` | `{ typedName, checkboxText, termsSnapshot?, investmentSnapshot? }` | Client formal acceptance. Records `clientAcceptance` and moves the document to `accepted`. |
| `POST` | `/api/v1/client-documents/[id]/sign` | `{ name, capacity, companyName?, signatureText, statement? }` | Admin-only PiB countersignature for `formal_acceptance` documents after publish. Records `providerSignature` and an approval row with `signatureSide: "provider"`. |

### Public (no auth)

| Method | Route | Notes |
|---|---|---|
| `GET` | `/api/v1/public/client-documents/[shareToken]` | Public share page data (status must be `client_review`+) |

### Public edit share (no auth wrapper — handles its own)

| Method | Route | Body | Notes |
|---|---|---|---|
| `POST` | `/api/v1/public/client-documents/edit/[editShareToken]/verify-code` | `{ code }` | Rate-limited 5/15min/IP. Sets `eds_{token}` cookie if code matches |
| `GET` | `/api/v1/public/client-documents/edit/[editShareToken]` | — | Returns doc if both code cookie + Firebase session cookie are present |

### Auth (for guest sign-in via magic link or Google)

| Method | Route | Body | Notes |
|---|---|---|---|
| `POST` | `/api/v1/auth/magic-link/send` | `{ email, redirectUrl?, context?, docTitle? }` | Rate-limited 3/15min/email. Sends branded sign-in email |
| `GET` | `/api/v1/auth/magic-link/verify?token=X` | — | Consumes magic link, redirects to /auth/magic-link/verify with customToken |
| `POST` | `/api/v1/auth/session` | `{ idToken }` | Exchanges Firebase ID token (from Google OAuth or magic-link landing) for session cookie |

---

## Messages Context Dock (mandatory when creating from chat)

When this run is inside Partners in Biz **Messages**, every create/version call must open the document side canvas.

1. Include `conversationId` + `responseMessageId` from the injected `[Messages dynamic chat — Context Dock / side canvas]` block (or `conversationOrigin`) on:
   - `POST /api/v1/client-documents`
   - `POST /api/v1/client-documents/[id]/versions`
2. The platform auto-attaches `open_context { kind: "document", id }` to the assistant message and returns `contextRef` + `uiActions`. Echo those in structured form if present.
3. **Never** paste raw JSON like `{"rich_parts":[{"type":"studio_artifact",...}]}` into chat. Client documents are **not** `studio_artifact` — canvas kind is always **`document`**.
4. **Never** dump the full document body as the only review surface. Humans review in the Context Dock (`DocumentContextPreview`).

---

## Default Agent Workflow

### Internal system/spec document → approval-gated kanban breakdown

Use this for substantial client work when Peet says to plan/spec something before implementation, especially coding, multi-agent work, operational setup, or anything that affects cost, timeline, scope, or the client's live assets.

1. Resolve the active relationship context first. If the current app page is a CRM company, use that company ID. If the context is only a selected client org, resolve its PiB-side platform CRM company when one exists.
2. Create the client document as `internal_draft` or `internal_review`. For CRM-company work, send `linked.companyId`; for system clients also include/verify `linked.clientOrgId`. Link to the active project with `linked.projectId` when a project exists. From Messages, always pass conversation handoff ids (see above).
3. Record assumptions on the document. Any assumption that changes scope, price, timeline, legal terms, final deliverables, or implementation direction must be `severity: "blocks_publish"`.
4. If there is any `blocks_publish` assumption, do not ask Peet to approve or publish the spec as ready. Return the admin URL and the blocking assumption(s) to resolve first.
5. Create a Pip approval-gate kanban task linked to the document/spec.
6. Break specialist work into project tasks only after the spec is approved, or create the tasks early but hold every agent task at `agentStatus: "awaiting-input"` with `dependsOn: [approvalTaskId]`. Set `agentEffort` deliberately when fanning out work: usually `high` for research/spec/architecture/ambiguous implementation, `medium` for QA/review/release checks, and `low` for routine status/reporting. Set `agentModel` only when Peet or the task needs a specific allowlisted model.
7. Important gotcha: project task creation may initialise agent tasks as `pending` even if `awaiting-input` was sent. Immediately PATCH each gated agent task back to `awaiting-input`, then verify with `GET /projects/[projectId]/tasks` before telling Peet the task fan-out is gated.
8. When Peet/PiB approves the spec, release the dependent agent tasks by patching them to `agentStatus: "pending"`; the kanban watcher then picks them up automatically. Do not manually start implementation before the approval gate is cleared.
9. After the document is sent to the client, fetch open comments and suggestions before acting on an approval. Treat unresolved client feedback as input to a new document version or a change-request task, not as noise.
10. Only release implementation tasks after client feedback is either incorporated, explicitly rejected with a reason, or converted into a blocker/change-request task.

### Client comments/suggestions → revised spec loop

When a shared spec has client feedback:

1. `GET /api/v1/client-documents/[id]/comments?status=open`
2. `GET /api/v1/client-documents/[id]/suggestions?status=open`
3. Summarise the feedback into: accepted changes, rejected changes with reasons, open blockers, and questions for Peet/client.
4. Create a new document version for accepted changes with `changeSummary` explaining the review pass.
5. Resolve comments only after the relevant document version or task exists.
6. If feedback changes implementation scope, update/hold/recreate kanban tasks before releasing agents.

### "Make a proposal for [Client]"

1. **Resolve relationship context:** prefer the current CRM company page/context. If not already on a company, find the organisation (`GET /api/v1/organizations?search=[client_name]`) and its PiB-side CRM company. For non-system CRM businesses, there is no `orgId`; use the company only.
2. **Pull context:** CRM company profile, linked org profile when present, open CRM deals, projects, wiki at `~/Cowork/Cowork/agents/partners/wiki/`
3. **Choose template:** proposal → `sales_proposal`, website/app → `build_spec`, etc.
4. **Create document:**
   ```
   POST /api/v1/client-documents
   X-Org-Id: <orgId>
   {
     "title": "[Client Name] — [Type] [Month YYYY]",
     "type": "sales_proposal",
     "templateId": "sales_proposal",
     "orgId": "<orgId if creating from org context>",
     "conversationId": "<from Messages canvas block when in chat>",
     "responseMessageId": "<from Messages canvas block when in chat>",
     "linked": {
       "companyId": "<crmCompanyId>",
       "clientOrgId": "<linkedOrgId if system client>",
       "dealId": "<dealId if known>"
     }
   }
   ```
   If you are creating directly from a CRM company page, `orgId` can be omitted; the API resolves the source org from `linked.companyId` and stamps `linked.clientOrgId` from the company relationship when available.
5. **Create first version** with filled blocks (you have all 23 block types available — see "Example Payloads" below):
   ```
   POST /api/v1/client-documents/[id]/versions
   X-Org-Id: <orgId>
   {
     "conversationId": "<from Messages canvas block when in chat>",
     "responseMessageId": "<from Messages canvas block when in chat>",
     "blocks": [ ...filled blocks array... ],
     "theme": {
       "brandName": "<org.name>",
       "palette": { "bg": "#0A0A0B", "text": "#F7F4EE", "accent": "#F5A623" },
       "typography": { "heading": "sans-serif", "body": "sans-serif" }
     },
     "changeSummary": "Initial agent-generated draft"
   }
   ```
   Use brand colors from org profile if available. When in Messages, expect `uiActions` / `contextRef` on the response and rely on the Context Dock — do not invent studio_artifact rich_parts.

   **Version payload tolerance (important):** each block should include `id`, `type`, `content`, `required` (boolean), and `display` (object, e.g. `{ "motion": "reveal" }`). If you omit `required` / `display`, the API defaults them (`required: false`, `display: {}`). Top-level `motion` is accepted as an alias for `display.motion`. Theme typography defaults when only `palette` is sent. Still prefer sending the full shape from the examples below. On any 400, read and surface the `error` string — do not retry blindly or hand off as "API rejects payload".
   5b. **If this is a proposal**, also include a `video` block (Loom intro), a `comparison` block, a `pricing_toggle` block, and an `faq` block for maximum impact. See "Make a Standout Proposal" below.
6. **Mark open assumptions:**
   ```
   PATCH /api/v1/client-documents/[id]
   {
     "assumptions": [
       { "id": "price", "text": "Investment amount TBC", "severity": "blocks_publish", "status": "open", "createdBy": "agent" },
       { "id": "timeline", "text": "Start date to confirm with client", "severity": "needs_review", "status": "open", "createdBy": "agent" }
     ]
   }
   ```
7. **Return to Peet:**
   - Admin URL: `https://partnersinbiz.online/portal/documents/[id]`
   - Summary of `blocks_publish` assumptions that must be resolved before you can publish
   - Never publish without Peet's explicit instruction

   **Success gate (mandatory before claiming done):**
   1. `GET /api/v1/client-documents/[id]/versions` and confirm the **current** version has filled content (not empty template strings).
   2. At least the primary blocks (`hero`/`summary` plus the sections you claimed to write) must be non-empty.
   3. If `POST …/versions` returns 400, surface the exact `error` string, fix the payload, and retry once. Never invent a success URL.
   4. Do not create additional document shells after a versions failure — update the existing document id.
   5. Only then return the portal URL. If verification fails, say the document shell exists but content is **not** landed.
8. **Publish/send to client:** only after blockers are resolved and Peet approves, call `POST /api/v1/client-documents/[id]/publish`. This moves the document to `client_review` and enables share. For system clients, verify both the PiB CRM company Documents tab and the client/org Documents list.
9. **Countersign proposals/SOWs when needed:** if Peet wants a visible PiB signature, use the admin document editor `Countersign` action or call `POST /api/v1/client-documents/[id]/sign` after publish. Default values are Peet Stander, Founder, The Partners in Business. The shared/rendered document appends an `Agreement signatures` section showing PiB signature state and the client's platform acceptance.

---

## Assumptions Guide

Use `assumptions[]` whenever context is incomplete. Severity:

| Severity | When to use |
|---|---|
| `blocks_publish` | Price, legal terms, binding dates, final scope, client name/address on contract |
| `needs_review` | Positioning copy, wording, references, estimates, optional sections |
| `info` | FYI notes that don't need action |

Always draft first. The document is safe to show Peet with open assumptions. Never publish (`POST .../publish`) without resolving all `blocks_publish` items first.

---

## Filling Blocks Well

**hero:** Write a one-line value proposition or document purpose as the subtitle. Example: `"A clear path to a faster, more discoverable web presence."`

**problem:** Describe the client's current situation and pain in 2–4 sentences. Be specific. Reference their industry, current tools, and what they're missing.

**scope:** Bullet list of what is included. Be explicit. Include tech stack, integrations, environments (staging + prod), etc.

**deliverables:** Concrete, countable outputs. "1 × Next.js website", "3 × Figma design rounds", "Monthly performance reports for 3 months".

**timeline:** Use realistic phase names: Discovery → Design → Build → QA → Launch. Include durations like "1 week", "2 weeks".

**investment:** Always in ZAR unless client is international. Include a line-item breakdown and a total. Add a `notes` field for payment schedule.

**terms:** Reference PiB standard: 50% upfront, 50% on launch. IP transfers on final payment. 30-day support post-launch.

**metrics:** For strategy docs: reach, engagement rate, follower growth, leads generated. For build docs: Lighthouse scores, Core Web Vitals, uptime.

---

## Example Payloads

Copy-paste-ready examples for every block type. Each block is one element of the `blocks` array sent to `POST /api/v1/client-documents/[id]/versions`.

**hero**

```json
{
  "id": "hero",
  "type": "hero",
  "title": "PROPOSAL",
  "content": "A performance-first advertising strategy built to fill your pipeline.",
  "required": true,
  "display": { "motion": "reveal" }
}
```

**summary**

```json
{
  "id": "summary",
  "type": "summary",
  "title": "Executive summary",
  "content": "Partners in Biz will run a 90-day Meta + Google Ads test designed to bring qualified leads into your pipeline at a target CPL of R220. We handle creative, copy, audiences, and reporting end-to-end so your team stays focused on closing.",
  "required": true,
  "display": { "motion": "reveal" }
}
```

**problem**

```json
{
  "id": "problem",
  "type": "problem",
  "title": "The problem",
  "content": "Your current channel mix relies heavily on referral and word of mouth. That cuts off at the same ~30 conversations a month, no matter how good the close rate is. To grow past your current ceiling you need a predictable, paid acquisition channel — and one that doesn't burn the brand to do it.",
  "required": true,
  "display": { "motion": "reveal" }
}
```

**scope**

```json
{
  "id": "scope",
  "type": "scope",
  "title": "What's included",
  "content": [
    "Meta Ads (Facebook + Instagram) full-funnel setup",
    "Google Ads search + Performance Max",
    "Pixel + conversion API install and QA",
    "5 ad creatives per month (static + 1 short-form video)",
    "Weekly performance reports + monthly strategy call"
  ],
  "required": true,
  "display": { "motion": "reveal" }
}
```

**deliverables**

```json
{
  "id": "deliverables",
  "type": "deliverables",
  "title": "Deliverables",
  "content": [
    "1 × Meta Ads Manager account setup",
    "1 × Google Ads account setup",
    "5 × creatives / month for 3 months",
    "12 × weekly performance reports",
    "3 × monthly strategy calls"
  ],
  "required": true,
  "display": { "motion": "reveal" }
}
```

**timeline**

```json
{
  "id": "timeline",
  "type": "timeline",
  "title": "Launch timeline",
  "content": {
    "phases": [
      { "label": "Week 1 — Setup", "duration": "7 days", "description": "Audience research, pixel install, creative briefs." },
      { "label": "Week 2 — Creative", "duration": "7 days", "description": "Ad creatives + ad copy approved and uploaded." },
      { "label": "Week 3 — Go live", "duration": "Day 1 of spend", "description": "Daily monitoring + budget pacing." }
    ]
  },
  "required": true,
  "display": { "motion": "timeline" }
}
```

**investment**

```json
{
  "id": "investment",
  "type": "investment",
  "title": "Investment",
  "content": {
    "items": [
      { "label": "Strategy + setup (one-off)", "amount": 18000, "currency": "ZAR" },
      { "label": "Monthly management fee", "amount": 12000, "currency": "ZAR" },
      { "label": "Monthly ad spend (managed)", "amount": 25000, "currency": "ZAR" },
      { "label": "Creative production", "amount": 6000, "currency": "ZAR" },
      { "label": "Reporting + strategy calls", "amount": 3000, "currency": "ZAR" }
    ],
    "total": 64000,
    "currency": "ZAR",
    "notes": "50% on signing, 50% on go-live. Month 2 and 3 invoiced on the 1st."
  },
  "required": true,
  "display": { "motion": "reveal" }
}
```

**terms**

```json
{
  "id": "terms",
  "type": "terms",
  "title": "Terms",
  "content": "Engagement runs for 90 days from go-live. Either party may exit with 30 days' written notice. Ad spend is billed at cost — no markup. All creative IP transfers to the client on final payment. PiB provides 30-day post-engagement support for handover.",
  "required": true,
  "display": {}
}
```

**approval**

```json
{
  "id": "approval",
  "type": "approval",
  "title": "Approve and proceed",
  "content": "By signing below, you accept this proposal and authorise Partners in Biz to begin work as scoped above.",
  "required": true,
  "display": {}
}
```

**metrics**

```json
{
  "id": "metrics",
  "type": "metrics",
  "title": "Success metrics — 90 days",
  "content": {
    "items": [
      { "label": "Qualified leads", "value": "0", "target": "180", "description": "Form fills with valid contact details" },
      { "label": "Cost per lead", "value": "0", "target": "220", "description": "Target CPL in ZAR" },
      { "label": "ROAS", "value": "0", "target": "4", "description": "Revenue / ad spend" }
    ]
  },
  "required": true,
  "display": { "motion": "counter" }
}
```

**risk**

```json
{
  "id": "risk",
  "type": "risk",
  "title": "Known risks and assumptions",
  "content": [
    "Initial CPL may run higher in week 1–2 while creatives are tested.",
    "Performance assumes the offer remains unchanged for the 90-day test.",
    "Lead quality depends on the website's intake form completion rate."
  ],
  "required": false,
  "display": { "motion": "reveal" }
}
```

**table**

```json
{
  "id": "table",
  "type": "table",
  "title": "Audience breakdown",
  "content": {
    "headers": ["Segment", "Size", "Channel"],
    "rows": [
      ["High-intent buyers", "120k", "Google Search"],
      ["Lookalikes of past clients", "1.2M", "Meta"],
      ["Re-engagement of warm list", "8k", "Meta + Email"]
    ]
  },
  "required": false,
  "display": {}
}
```

**gallery**

```json
{
  "id": "gallery",
  "type": "gallery",
  "title": "Sample creatives",
  "content": [
    "https://placehold.co/800x800/png?text=Creative+1",
    "https://placehold.co/800x800/png?text=Creative+2",
    "https://placehold.co/800x800/png?text=Creative+3"
  ],
  "required": false,
  "display": {}
}
```

**callout**

```json
{
  "id": "callout-guarantee",
  "type": "callout",
  "title": "",
  "content": {
    "title": "Our guarantee",
    "body": "If we don't hit your target CPL in 60 days, we work month 3 for free until we do.",
    "variant": "success"
  },
  "required": false,
  "display": { "motion": "reveal" }
}
```

**rich_text**

```json
{
  "id": "notes",
  "type": "rich_text",
  "title": "A note from Peet",
  "content": "We've run this exact playbook for 5 SaaS clients in the last 18 months. Every one hit the CPL target inside 60 days. The reason: we ship creative weekly, not monthly — so we kill bad ads fast and double down on what works.",
  "required": false,
  "display": {}
}
```

**image**

```json
{
  "id": "team-photo",
  "type": "image",
  "title": "",
  "content": {
    "url": "https://placehold.co/1600x900/png?text=PiB+Team",
    "alt": "The Partners in Biz team",
    "caption": "Your dedicated team: Peet (strategy), Sarah (creative), Tom (media buyer)",
    "width": "wide"
  },
  "required": false,
  "display": { "motion": "reveal" }
}
```

**video**

```json
{
  "id": "loom-intro",
  "type": "video",
  "title": "A quick hello from Peet",
  "content": {
    "url": "https://www.loom.com/share/abc123def456",
    "provider": "loom",
    "caption": "3 minutes — what we'll do and why we think it'll work."
  },
  "required": false,
  "display": { "motion": "reveal" }
}
```

**embed**

```json
{
  "id": "book-call",
  "type": "embed",
  "title": "Book a kickoff call",
  "content": {
    "url": "https://calendly.com/peetstander/30min",
    "height": 700,
    "caption": "Pick a time that works — we'll lock in week 1."
  },
  "required": false,
  "display": {}
}
```

**link_card**

```json
{
  "id": "case-study",
  "type": "link_card",
  "title": "Case study",
  "content": {
    "url": "https://partnersinbiz.online/case-studies/saas-x",
    "title": "How SaaS X cut CPL by 47% in 60 days",
    "description": "Same playbook, same team, same channels. Full write-up with the actual ad creatives that won.",
    "image": "https://placehold.co/1200x630/png?text=Case+Study",
    "favicon": "https://partnersinbiz.online/favicon.ico"
  },
  "required": false,
  "display": { "motion": "reveal" }
}
```

**chart**

```json
{
  "id": "spend-allocation",
  "type": "chart",
  "title": "Proposed spend allocation",
  "content": {
    "kind": "pie",
    "data": [
      { "name": "Meta Ads", "value": 15000 },
      { "name": "Google Search", "value": 7000 },
      { "name": "Performance Max", "value": 3000 }
    ],
    "title": "Monthly ad spend by channel"
  },
  "required": false,
  "display": { "motion": "reveal" }
}
```

**pricing_toggle**

```json
{
  "id": "addons",
  "type": "pricing_toggle",
  "title": "Optional add-ons",
  "content": {
    "items": [
      { "label": "Base package (90 days)", "amount": 64000, "required": true, "default": true },
      { "label": "Landing page design + build", "amount": 18000, "default": false },
      { "label": "Email nurture sequence (7 emails)", "amount": 9000, "default": false },
      { "label": "Sales call coaching (4 sessions)", "amount": 12000, "default": false }
    ],
    "currency": "ZAR",
    "note": "Toggle any add-on above to see the new total. We'll lock the final scope on the kickoff call."
  },
  "required": false,
  "display": {}
}
```

**faq**

```json
{
  "id": "faq",
  "type": "faq",
  "title": "Frequently asked questions",
  "content": {
    "items": [
      { "q": "What if we don't hit the CPL target?", "a": "We work month 3 for free until we hit it. Locked in writing." },
      { "q": "Who owns the ad accounts and creative?", "a": "You do — from day one. All accounts are on your billing, all creative IP transfers on payment." },
      { "q": "Can we pause if it isn't working?", "a": "Yes. 30 days' written notice and we wrap up — no penalty, no clawback." },
      { "q": "Why not in-house?", "a": "By month 6 you'll have learned everything you need and can hire in-house at lower cost. We're happy to brief your future hire." }
    ]
  },
  "required": false,
  "display": { "motion": "reveal" }
}
```

**comparison**

```json
{
  "id": "vs-alternatives",
  "type": "comparison",
  "title": "PiB vs the alternatives",
  "content": {
    "headers": ["", "PiB (this proposal)", "In-house hire", "Other agency"],
    "rows": [
      { "label": "Time to first leads", "values": ["Week 3", "Month 2-3", "Month 1-2"] },
      { "label": "Monthly cost", "values": ["R12k mgmt + R25k spend", "R45k+ salary + tools", "R20k-R35k+"] },
      { "label": "Weekly creative refresh", "values": [true, false, false] },
      { "label": "Direct line to senior strategist", "values": [true, true, false] },
      { "label": "Exit on 30 days' notice", "values": [true, false, false] },
      { "label": "Guarantee on CPL", "values": [true, false, false] }
    ],
    "highlightCol": 1
  },
  "required": false,
  "display": { "motion": "reveal" }
}
```

---

## Make a Standout Proposal

Default proposals are fine. *Standout* proposals close. When generating a `sales_proposal`, layer in these blocks for outsized impact:

1. **Lead with a video block** (Loom intro from Peet) — placed right after the hero. A 60–180s personal walkthrough is hugely differentiating. Use `provider: 'loom'` and put it before the `summary` block.
2. **Use a comparison block** to anchor against alternatives. "PiB vs in-house hire vs other agency" or "DIY vs done-for-you." Highlight the PiB column with `highlightCol: 1` so it visually wins.
3. **Use pricing_toggle for upsells / optional add-ons.** The client toggles add-ons live and watches the total update — it makes optional spend feel like a choice, not a push. Always mark the base package `required: true, default: true`.
4. **Use an faq block** to pre-empt the top 3–5 objections **before** the approval block. Common ones: "what if it doesn't work?", "who owns the IP?", "can we pause?", "why not in-house?". Answering them in writing removes the last reason to delay.
5. **Investment block auto-renders an allocation chart** when there are 2+ line items — so just put 5 line items in and it'll look great with no extra effort. Aim for: setup, monthly fee, ad spend, creative, reporting.
6. **Metrics block auto-renders progress rings** when both `value` and `target` are set. Use this for "current vs target" stat displays — perfect for the "what we'll hit" section. **IMPORTANT: `value` and `target` MUST be strings (`"0"`, `"180"`), NOT integers (`0`, `180`). The renderer calls `.replace()` on these values and will crash with `TypeError: e.replace is not a function` if you pass integers.**
7. **Set `motion: 'counter'` on metrics blocks** so numbers animate from 0 → final value on scroll. Set `motion: 'reveal'` on prose blocks (summary, problem, scope, deliverables, callout, risk). Set `motion: 'timeline'` on the timeline block for sequential phase reveal.

**Recommended order for a standout sales proposal:**
1. `hero` (motion: reveal)
2. `video` — Loom intro
3. `summary` (motion: reveal)
4. `problem` (motion: reveal)
5. `scope` (motion: reveal)
6. `deliverables` (motion: reveal)
7. `comparison` — PiB vs alternatives
8. `timeline` (motion: timeline)
9. `metrics` (motion: counter) — what we'll hit
10. `investment` — 5 line items so the chart auto-renders
11. `pricing_toggle` — optional add-ons
12. `callout` — guarantee / risk reversal
13. `faq` — objections pre-empted
14. `terms`
15. `approval`

---

## Cross-References

- **research-intelligence** skill creates structured `research_items` first. Use `research_report` documents only when research needs polished client presentation, approval, or shareable output. Link reports with `linked.researchItemIds`.
- **content-engine** skill creates `content_campaign_plan` documents automatically
- **project-management** skill links documents to projects via `linked.projectId`
- **crm-sales** skill links proposals to deals via `linked.dealId`
- **crm-sales/company context** links documents to CRM companies via `linked.companyId`; system-client visibility also needs `linked.clientOrgId`.
- **seo-sprint-manager** skill can link sprint reports via `linked.seoSprintId`

---

## Sharing a document with a client (recommended flow)

After creating a proposal/spec/report draft:

1. If the client just needs to read: publish the document. Share `https://partnersinbiz.online/d/<shareToken>` — public, no friction.
2. If you want them to comment / approve / suggest changes:
   - Enable edit share: `POST /api/v1/client-documents/[id]/edit-share/enable`
   - Copy the URL (`/d/<editShareToken>/edit`) and the access code from the response
   - Send them both — typically the URL in your message and the code in a separate channel for some belt-and-braces security
   - They sign in via magic link or Google, then have whatever permissions the document allows
3. Watch the access log (`GET /api/v1/client-documents/[id]/access-log`) to see who's viewed + when
4. Comments + suggestions show up in the document's review rail in admin
5. Revoke at any time: regenerate the code, or disable the share entirely
