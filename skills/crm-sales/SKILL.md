---
name: crm-sales
description: >
  Run the full CRM operating system on Partners in Biz: companies, contacts, leads, deals, pipeline,
  quotes, proposals, company command centers, business relationships, service workspaces, orders,
  shipments, inventory, activity logging, AI-generated contact briefs, public lead-capture forms,
  form submission triage, dynamic contact segments, CRM integrations (Mailchimp, HubSpot, Google
  Contacts), capture source attribution, and bulk contact import.
  Use this skill whenever the user mentions anything related to sales or CRM, including but not limited
  to: "add a contact", "new lead", "import contacts", "bulk import", "CSV import", "tag contact",
  "remove tag", "filter by tag", "qualify lead", "convert lead to client", "contact brief",
  "brief me on this contact", "AI contact summary", "new deal", "create deal",
  "move deal to negotiation", "deal stage", "close deal", "deal won", "deal lost", "win rate",
  "pipeline value", "pipeline report", "log a call", "log email", "activity history", "draft a quote",
  "send proposal", "create proposal", "quote accepted", "quote rejected", "convert quote to invoice",
  "create a form", "lead form", "contact form", "form submissions", "new form submission",
  "review submissions", "schedule meeting with contact", "task for this deal", "comment on contact",
  "comment on deal", "leave a note on deal", "@mention sales rep", "sales notification",
  "create segment", "dynamic list", "audience segment", "resolve segment", "who is in this segment",
  "company command center", "business relationship", "supplier company", "service workspace",
  "SEO workspace", "order", "shipment", "inventory", "quote to delivery", "CRM OS dashboard",
  "reconcile CRM links", "connect Mailchimp", "connect HubSpot", "sync contacts", "CRM integration",
  "capture source", "lead source", "where did this contact come from", "attribution",
  "retainer", "recurring client", "won this month", "lost this month", "sales operating system".
  If in doubt, trigger — this skill owns the full company-to-delivery lifecycle.
  For retainer vs deal vs invoice semantics, also load `sales-operating-system`.
---

# CRM & Sales — Partners in Biz Platform API

Covers the full sales funnel: contacts (leads → prospects → clients → churned), deals with stages, activity logging, quotes/proposals, AI contact briefings, and public lead-capture forms with submission triage.

**Commercial OS (Blake):** deals win/change relationships; invoices collect money; retainers are **not** a deal every month. Full rules live in skill `sales-operating-system`. Dashboard `wonThisMonth` / `lostThisMonth` are deal heuristics (`probability === 100` / `lostReason` + `updatedAt` in the current calendar month) — paid invoices do not count as wins.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## Base URL & Authentication

```
https://partnersinbiz.online/api/v1
```

```
Authorization: Bearer <AI_API_KEY>
```

Prefer the user-delegation Bearer token (`pib_dlg_…`) or a device-login / personal token from `pib-skills login` (see `system-auth`). `AI_API_KEY` is for cron/system jobs only. On 403, print the API error and stop — do not retry with a god-key.

Except for `POST /forms/[slug]/submit` which is **public** (no auth required).

## Client Document Handoff

Sales opportunities that need client review should produce Sales Proposal documents through the `client-documents` skill. Link them with `linked.dealId`, keep pricing/legal/scope assumptions as `blocks_publish` until resolved, and use formal acceptance for proposal approval.

Prospect, company, account, stakeholder, and market-fit research should be captured in the Research module through the `research-intelligence` skill and linked to the relevant deal, company, contact, project, or proposal.

## Cross-workspace CRM relationship model

CRM Companies and Contacts are now the bridge between one workspace and another business that later joins PiB.

- A sender workspace can create a CRM Company/Contact, then send an invoice or share a project with `companyId` and/or `contactId`.
- Secure public claim links use `claimable_relationships` to connect `sourceOrgId/sourceCompanyId/sourceContactId` to `targetOrgId/targetUserId` after signup or sign-in.
- Sender-owned CRM links are relationship metadata only: `companies.linkedOrgId` and `contacts.linkedUserId` do not grant the sender admin rights inside the recipient workspace.
- **These two fields are server-set only.** They are in `NEVER_FROM_BODY` and are silently dropped from any create/update payload. Writing them requires an accepted partner invite (below) or the platform-owner sync. Do not attempt to set them directly — the call will appear to succeed and the field will be absent.

### Partner Links (org ↔ org)

Any org can invite a company or contact from its own CRM to link workspaces. On accept both sides are wired up mutually.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/crm/partner-invites` | GET, POST | List invites; create + email one. Body: `{ kind: 'company'\|'contact', companyId, contactId?, email?, name?, companyName?, message?, capabilities? }` |
| `/api/v1/crm/partner-invites/{id}` | GET, PATCH | PATCH `{ action: 'revoke' \| 'resend' }` |
| `/api/v1/public/partner-invites/{token}` | GET, POST | Public preview / accept / decline. POST `{ action: 'accept'\|'decline', displayName?, businessName?, password?, orgId?, preferTargetCompanyId? }` |
| `/api/v1/crm/partner-links` | GET | Established links + invitations in flight (powers `/portal/partners`) |
| `/api/v1/crm/partner-links/{relationshipId}` | PATCH | Edit what **your** side shares: `sharedCapabilities`, `fieldSharingPolicy`, `portalVisible`, `relationshipType`. One-sided by design — never writes the counterpart row. |
| `/api/v1/crm/partner-links/{relationshipId}/unlink` | POST | Sever from either side |
| `/api/v1/crm/partner-shares` | GET, POST | List (`?direction=outgoing\|incoming\|both`) / share one record. POST `{ relationshipId, resourceType, resourceId, permission? }` |
| `/api/v1/crm/partner-shares/searchable` | GET | `?type=project&q=…&relationshipId=…` — records you could share, for the picker. Flags rows already shared with that partner. |
| `/api/v1/crm/partner-shares/{id}` | GET, PATCH, DELETE | GET returns the shared record (**either** side); PATCH `{ permission: 'view'\|'comment' }` (owning org only); DELETE revokes (owning org only) |
| `/api/v1/crm/partner-shares/{id}/comments` | GET, POST | Conversation on a shared record |
| `/api/v1/crm/partner-shares/{id}/comments/{commentId}` | DELETE | Soft-delete your own org's comment |

Accept semantics:
- Invites are **never** auto-accepted, even when both orgs already exist — unlike `claimable_relationships`, which auto-claims when `linkedOrgId` is already set.
- Acceptable by the invited email, or by an owner/admin of an org that email already belongs to (forwarding case).
- On accept: the inviter's company gets `linkedOrgId`; a contact matching `recipientEmail` gets `linkedUserId` (created if none); a mirror company + contact are created in the acceptor's CRM; two `businessRelationships` rows are written with `relationshipType: 'partner'` sharing one `partnerLinkId`.
- Unlink revokes both relationship rows and clears the pointers on both sides. The CRM companies and contacts survive.
- Tokens expire after 30 days. `GET /api/v1/inbox` surfaces pending invites addressed to the signed-in user (`itemType: 'partner_invite'`).
- If the acceptor has no account, one is created and a new org is provisioned with them as `owner`. If they already belong to orgs they pick which one links — and their existing role is never rewritten.

**Where a link is visible in the CRM:** `components/crm/SystemLinkBadge.tsx` renders a "Linked workspace" pill on the company row + company header (`companies.linkedOrgId`) and a "Linked user" pill on the contact command center (`contacts.linkedUserId`). Both admin CRM detail pages carry the same badges. The portal management surface is `/portal/partners` (CRM subnav → Partners): invite form, linked partners with sharing editor / share-record / unlink, invitations with resend/revoke, and shared-record lists. A company with no linked workspace shows an "Invite … to link workspaces" CTA on its command center that deep-links to `/portal/partners?companyId=…`.

### Per-record sharing (`partner_record_shares`)

On top of the link, an org can share ONE specific record with the partner: `deal`, `project`, `invoice`, `quote`, or `client_document`.

- **Capability-gated.** A record type can only be shared when the link's `sharedCapabilities` already include the mapped capability (deal→`crm`, project→`projects`, invoice/quote→`invoices`, client_document→`documents`). Edit that with the PATCH endpoint above first.
- **Ownership-checked.** You can only share a record whose `orgId` is your org.
- **Whitelisted reads.** `GET /api/v1/crm/partner-shares/{id}` returns a per-type field whitelist, never the raw document — arbitrary fields on the source record do not leak.
- **Idempotent.** Re-sharing the same record returns the existing active row.
- **Revocation is layered:** revoke a single share, or unlink the partnership — unlinking calls `revokeSharesForPartnerLink` and every share riding on that `partnerLinkId` dies with it. Reads also re-check that the link is still active, so a severed link kills access even for shares that were never individually revoked.
- Viewer UI: `/portal/partners/shared/{shareId}` — reachable by **both** sides (`viewerRole: 'owner' | 'partner'`), so the owner has a surface for the conversation too.

**`permission` is enforced, not decorative.** `view` (default) is read-only; `comment` lets the receiving org post on the thread. The owning org can always comment on its own record. Change it any time with PATCH; the partner gets a notification either way. Comments live in `partner_share_comments`, are readable by both sides only, and each org can soft-delete only its own. Unlinking or revoking the share makes the whole thread inaccessible (`resolveShareAccess` re-checks share status *and* link status on every read).

**Picking a record to share:** use `components/crm/PartnerRecordPicker.tsx` (debounced search over `/searchable`), not a raw id. Search runs two passes and merges them — a server-side **prefix** range query on the type's title field (scales to any corpus), plus a bounded 500-row window filtered in memory for **mid-string** matches. When that window fills, the response carries `truncated: true` and the picker says so rather than silently dropping matches. Requires the `orgId + <titleField>` index per type (deals.title, projects.name, invoices.invoiceNumber, quotes.quoteNumber, client_documents.title). Note that `orderBy` excludes documents missing that field, so an untitled record will not appear.

**Sharing from the record itself:** `components/crm/ShareWithPartnerButton.tsx` is a drop-in control already mounted on the project workspace header, deal detail drawer, quote detail, invoice detail, and client-document detail. It lists only partners whose link already shares the matching capability and explains why the rest are hidden, so the capability gate is visible before submit rather than as a server error.

**Comment emails:** a new comment also emails the *other* org's `settings.notificationEmail` (falling back to `billingEmail`) via `partnerShareCommentEmail`, because a partner in another workspace will not be watching this org's notification bell. Send failures are logged and never fail the comment.

**Cross-org read policy:** there are exactly two sanctioned cross-org read locations — `lib/companies/command-center.ts` (aggregate counts/statuses for a linked company) and `lib/partner-links/shares.ts` (one record named by an active share row). Anything else is a spec violation.
- For PiB-issued resources, `pib-platform-owner` is the canonical source/issuer org and the client org is the recipient/target org. Platform CRM Companies are deduped by `linkedOrgId`; platform CRM Contacts are deduped by `linkedUserId`, then email.
- Future PiB invoices, quotes, and projects to a linked client org should reuse the existing platform CRM Company and write `companyId/sourceCompanyId`.
- Client-created project requests remain client-originated until PiB accepts or converts them into PiB-sourced work.

Use `lib/platform-owner/relationships.ts` in app code when syncing PiB's platform-owner CRM with client orgs/members. Use the dry-run scripts before touching existing data: `scripts/migrate-pib-owned-client-resources.ts`, `scripts/backfill-platform-owner-crm-relationships.ts`, and `scripts/backfill-platform-owner-resource-company-links.ts`.

## CRM operating system command center

The company detail page is now the main CRM operating surface. The portal route `/portal/companies/[id]` loads `GET /api/v1/crm/companies/[id]/command-center` and renders one company command center with overview, contacts, deals, projects, documents, service workspaces, relationships, quotes, invoices, orders, shipments, inventory, analytics, and activity.

Project visibility from a company must be index-safe. The command center reads projects by `orgId == company.orgId`, then filters in memory by `companyId`, `sourceCompanyId`, company id arrays, `recipientOrgId`/`targetOrgId`/`clientOrgId`/`legacyOrgId`/`linkedOrgId`, `allowedOrgIds`, and active `businessRelationships` (`relationshipId`, related company ids, and target org ids). Do not add composite-index-sensitive chained Firestore queries for this surface.

New CRM OS APIs:

- `GET /crm/companies/[id]/command-center`
- `GET /admin/crm/companies/[id]/command-center?orgSlug=<slug>` for selected-client admin views
- `GET /crm/companies/[id]/projects`
- `GET/POST/PATCH /crm/relationships`
- `GET/POST/PATCH /service-workspaces`
- `GET/POST/PATCH /orders` (`PATCH` uses `?id=<orderId>`)
- `GET/POST/PATCH /shipments` (`PATCH` uses `?id=<shipmentId>`)
- `GET/POST/PATCH /inventory-items` (`PATCH` uses `?id=<inventoryItemId>`)
- `POST /crm/reconcile-links`
- `GET /crm/os-dashboard`
- `GET/POST /crm/data-tools`
- `GET/PUT /crm/setup`
- `POST /crm/setup/apply-template`
- `GET/POST /crm/saved-views`
- `DELETE /crm/saved-views/[id]`
- `GET/POST /crm/webhooks`
- `GET/PUT/DELETE /crm/webhooks/[id]`
- `POST /crm/webhooks/[id]/enable`
- `POST /crm/webhooks/[id]/disable`
- `POST /crm/webhooks/[id]/rotate-secret`
- `POST /crm/webhooks/[id]/test`
- `GET /crm/notifications`
- `POST /crm/notifications/mark-read`

Current contact quick-action routes:

| Method | Route | Use |
|---|---|---|
| `GET` | `/crm/contacts/[id]/activities` | Contact activity timeline. |
| `GET` | `/crm/contacts/[id]/facts` | ContactFact evidence ledger. |
| `POST` | `/crm/contacts/[id]/facts/[factId]/decide` | Accept or dismiss a proposed fact. |
| `GET` | `/crm/contacts/[id]/field-history` | Collapsed field history from ContactFacts. |
| `GET` | `/crm/contacts/[id]/enrollments` | Contact sequence enrollments. |
| `POST` | `/crm/contacts/[id]/send-email` | Human send/log a CRM-scoped email. Agents must draft/review only. |
| `POST` | `/crm/contacts/[id]/send-sms` | Send/log a CRM-scoped SMS. |
| `POST` | `/crm/contacts/[id]/schedule-meeting` | Create a contact-linked meeting/calendar event. |
| `POST` | `/crm/contacts/[id]/recompute-score` | Recompute engagement/lead score for one contact. |
| `GET` | `/crm/contacts/[id]/suggestions` | Agent/CRM suggestions for the contact. |
| `POST` | `/crm/contacts/[id]/tags` | Add/update contact tags. |

Object CRUD for companies, contacts, deals, segments, and sequences lives on `/api/v1/crm/{companies,contacts,deals,segments,sequences}`. Growth OS (`/crm/growth-os/*`) is a product layer (desk, ingest, review queue) that must call those same object APIs rather than a second store. Lists created in Growth also write a `segments` alias (`autoRefresh: false`). Chat-authored sequences persist as **draft** sequences with **no enrollments**. Do not treat LinkedIn as a mailbox. Do not call human `send-email` as unrestricted agent send — draft via `/agent/email/drafts` or Growth outbound, then wait for human Approve & send.

CRM report routes:

| Method | Route | Use |
|---|---|---|
| `GET` | `/crm/reports/activity-summary` | Activity counts and recency. |
| `GET` | `/crm/reports/forecast` | Forecast by stage/close window. |
| `GET` | `/crm/reports/funnel` | Funnel conversion data. |
| `GET` | `/crm/reports/pipeline-velocity` | Stage velocity and cycle-time signals. |
| `GET` | `/crm/reports/rep-performance` | Sales rep performance rollup. |

New collections/modules:

- `businessRelationships`: explicit B2B links between source and target org/company records, including `relationshipType`, `status`, `sharedCapabilities`, `portalVisible`, `visibility`, `allowedOrgIds`, `allowedUserIds`, `approvalState`, and `fieldSharingPolicy`.
- `serviceWorkspaces`: company-scoped delivery workspaces for `seo`, `geo_seo`, `properties`, `social`, `ads`, `email`, `documents`, `support`, or `custom` service lines. Link them to company/contact/project/document/report/task/approval/invoice/analytics records where possible.
- `orders`, `shipments`, `inventoryItems`: ERP-lite quote-to-delivery records. Use existing projects as the execution layer; commerce records link into projects and service workspaces rather than replacing Kanban/project work.

When PiB links a client org, `ensurePlatformCompanyForOrg` now keeps both sides visible:

- Platform owner org gets/updates the client CRM Company (`linkedOrgId=<clientOrgId>`).
- The client org gets/updates a CRM Company representing Partners in Biz (`source='reciprocal_platform_supplier'`, `visibility='client_visible'`, `allowedOrgIds=[clientOrgId, platformOrgId]`).
- Reciprocal `businessRelationships` are created/updated: platform `customer` relationship and client `supplier` relationship, both `client_visible` and portal-visible.

Agents may suggest, draft, reconcile, create tasks/documents, and prepare CRM updates. Any agent action that is client-visible, destructive, billing-related, or changes sharing/visibility must return or create a pending approval state instead of applying the change directly unless `approvalState='approved'`.

Hardening rules from the CRM OS follow-up:

- Selected-client admin company route is `/admin/org/[slug]/crm/companies/[id]`, backed by `GET /api/v1/admin/crm/companies/[id]/command-center?orgSlug=<slug>`. Admin routes use selected-client access checks; portal routes use the portal command-center endpoint.
- Portal/company command-center data must pass through `filterCompanyCommandCenterForVisibility`. It hides `internal`/`private` rows unless explicitly allowed by `allowedOrgIds`/`allowedUserIds`, and enforces active relationship `fieldSharingPolicy` for contacts, projects, documents, commerce, and analytics.
- `POST /crm/reconcile-links` defaults to dry-run. Apply mode must include `{"mode":"apply","approved":true}` after a reviewed dry-run report. Do not run apply mode speculatively.
- When a quote transitions to `accepted`, `createFulfillmentForAcceptedQuote` creates the confirmed order, pending shipment, reserved inventory movement, audit event, notification, and quote fulfillment links. Do not manually duplicate fulfillment records unless reconciling a failed partial write.
- `/crm/data-tools` is for admin export, dry-run import, approved import, and dedupe review across companies, contacts, relationships, products, and inventory. Import apply mode requires `approved:true`.
- Relationship, service workspace, shipment, commerce approval, and quote fulfillment changes write `crmAuditEvents`; shipment and approval-sensitive changes also create notifications.
- Commerce/service writes are guarded by `guardAgentCrmAction`. If an agent request changes billing, client-visible delivery state, or visibility without approved state, expect a `202` response `{ approvalRequired: true, reason }`; create or update a project/client-document approval rather than retrying blindly.

## Auth & org scoping (PR 2+)

All `/api/v1/crm/contacts/*` routes now use the `withCrmAuth` middleware:
- **User-delegation Bearer token (interactive agent calls):** `Authorization: Bearer pib_dlg_…` + `X-Org-Id: <orgId>` header. Role resolves to the delegating human's own `orgMembers/{orgId}_{uid}` role — it does **not** bypass `minRole` or permission toggles. This is the default for human-triggered Hermes runs; see `system-auth`.
- **Agent system key (cron/system only):** `Authorization: Bearer ${AI_API_KEY}` + `X-Org-Id: <orgId>` header. Role is `system` for unattended/cron jobs only — do not use this path for interactive work.
- **Session cookie (portal users):** `__session` cookie. Role resolved from `orgMembers/{orgId}_{uid}`. Routes enforce `viewer`/`member`/`admin` minRole.
- The `orgId` body field on POST is IGNORED — middleware reads orgId from the token. Always send `X-Org-Id` for Bearer calls.
- Every write embeds `createdByRef` / `updatedByRef` snapshots. Agent calls show as `Pip` (`uid: 'agent:pip', kind: 'agent'`) when using the system key; delegated calls attribute to the delegating human.

## orgId conventions

- `contacts`, `deals`, `activities`, `quotes`, `forms`, `form_submissions` all carry `orgId` as a field.
- **Contacts routes:** orgId is read from auth middleware, not the POST body. For Bearer calls, send `X-Org-Id: <orgId>` header instead.
- **Deals, quotes, forms, activities:** still require `orgId` in the POST body. Legacy routes not yet migrated to `withCrmAuth`.
- For filters on GET: pass `?orgId=X` as query param (deals, quotes, forms). Contacts GET uses `X-Org-Id` for Bearer calls.

## Collaboration primitives

- **Idempotency**: see the `## Idempotency` section below — CRM POST routes do NOT generally honour an `Idempotency-Key` header
- **Comments** (`resourceType: 'contact' | 'deal' | 'quote' | 'form_submission'`): leave internal notes with `@user:<uid>` / `@agent:<id>` mentions
- **Tasks** linked to contacts/deals: `POST /tasks` with `contactId` / `dealId` — see `project-management` skill
- **Calendar events** linked to contacts/deals: `POST /calendar/events` with `relatedTo: { type: 'contact'|'deal', id }` — see `project-management` skill

## Response envelope

```json
{ "success": true, "data": { ... }, "meta": { "total": 50, "page": 1, "limit": 20 } }
```

## Idempotency

CRM POST routes do NOT honour an `Idempotency-Key` header. Duplicate POSTs may create duplicate records.

**Mitigations in place:**
- **Quotes** — atomic `runTransaction` quote numbering (no duplicate quote numbers under concurrency)
- **Forms** — slug uniqueness per-org enforced (duplicate POST with same slug → 409)
- **Form submissions** (`/forms/[id]/submit` public route) — deduped via IP rate-limiting

**Not deduped:**
- Contacts, Deals, Segments, Integrations, Capture-sources — duplicate POSTs create duplicates. Callers should retry POST only after confirming the previous call did NOT succeed (check response, or query for the record).

This is a deliberate decision (Sub-1 cleanup). To restore idempotency in a future PR, add `withIdempotency` wrapping around the relevant POST handlers.

## DELETE response shape

All CRM DELETE endpoints return `apiSuccess({ id })` on success (HTTP 200). Forms previously returned `{ id, deleted: true }` — standardized in PR 8.

```ts
// Response body:
{ success: true, data: { id: "<deleted-id>" } }
```

For Forms, `?force=true` triggers hard-delete; default is soft-delete (`deleted: true, active: false` set on doc). The response is the same `{ id }` in both cases.

---

## API Reference

### Contacts

#### `GET /crm/contacts` — auth: cookie (viewer+) or Bearer + X-Org-Id
List contacts with filters.

Query params:
- `stage` — `new`|`contacted`|`replied`|`demo`|`proposal`|`won`|`lost`
- `type` — `lead`|`prospect`|`client`|`churned`
- `source` — `manual`|`form`|`import`|`outreach`
- `tags` — comma-separated (array-contains-any, max 10)
- `search` — name/email/company contains (in-memory after fetch)
- `page` (default 1), `limit` (default 50, max 200)

Response: array of `Contact`:
```json
{ "id": "contact_abc", "orgId": "org_xyz", "name": "Jane Doe", "email": "jane@acme.com",
  "phone": "+27...", "company": "Acme", "website": "https://acme.com",
  "source": "form", "type": "lead", "stage": "new",
  "tags": ["enterprise", "south-africa"], "notes": "...", "assignedTo": "user_123",
  "createdAt": "...", "updatedAt": "...", "lastContactedAt": null, "deleted": false }
```

#### `POST /crm/contacts` — auth: cookie (member+) or Bearer + X-Org-Id
Required: `name`, `email` (valid). Defaults: `source='manual'`, `type='lead'`, `stage='new'`, `tags=[]`.

`orgId` is read from the auth middleware — do NOT include it in the POST body. For Bearer calls, send `X-Org-Id: <orgId>` as a request header.

Body:
```json
{
  "name": "Jane Doe",
  "email": "jane@acme.com",
  "phone": "+27...",
  "company": "Acme",
  "website": "https://acme.com",
  "source": "form",
  "type": "lead",
  "stage": "new",
  "tags": ["enterprise"],
  "notes": "Met at conference",
  "assignedTo": "user_123"
}
```

Response (201): `{ "id": "contact_abc" }`. Dispatches `contact.created` webhook when `orgId` present.

#### `GET /crm/contacts/[id]` — auth: cookie (viewer+) or Bearer + X-Org-Id
Full contact.

#### `PUT /crm/contacts/[id]` — auth: cookie (member+) or Bearer + X-Org-Id
Update any contact field. Records `updatedAt`. Dispatches `contact.updated` webhook.

#### `DELETE /crm/contacts/[id]` — auth: cookie (member+) or Bearer + X-Org-Id
Soft-delete (`deleted: true`). Members blocked if `membersCanDeleteContacts` permission toggle is off.

#### `GET /crm/contacts/[id]/activities` — auth: cookie (viewer+) or Bearer + X-Org-Id
Activity timeline for this contact. Sorted `createdAt desc`.

#### `POST /crm/contacts/[id]/activities` — auth: cookie (member+) or Bearer + X-Org-Id
Log activity. Body: `{ type, summary, dealId?, metadata? }`. `type`: `email_sent`|`email_received`|`call`|`note`|`stage_change`|`sequence_enrolled`|`sequence_completed`.

#### `POST /crm/contacts/[id]/tags` — auth: cookie (member+) or Bearer + X-Org-Id
Atomic tag update. Body: `{ add?: string[], remove?: string[] }`. Uses Firestore `arrayUnion` / `arrayRemove`. Returns `{ id, tags }` (post-update).

#### `GET /contacts/[id]/preferences` — auth: viewer
Fetch communication preferences for a contact (email opt-in/out, SMS, notification channels).

#### `PUT /contacts/[id]/preferences` — auth: member
Update communication preferences. Partial updates accepted — only supplied fields change.

### Deals

> **Breaking change — A3 strict cutover:** `Deal.stage: DealStage` has been **removed**. Deals now carry `pipelineId: string` + `stageId: string`. Any external integration that reads `deal.stage` must be updated to resolve stage via `pipelineId` + `pipeline.stages.find(s => s.id === stageId)` for label / kind / color / probability.

#### `GET /crm/deals` — auth: viewer
Filters: `pipelineId`, `stageId`, `contactId`, `page`, `limit`.

Response: array of `Deal`:
```json
{ "id": "deal_xyz", "orgId": "org_abc", "contactId": "contact_abc",
  "title": "Acme - Pro Plan - Annual", "value": 12000, "currency": "ZAR",
  "pipelineId": "pipe_abc", "stageId": "stage_open_1",
  "expectedCloseDate": "2026-05-30", "notes": "...",
  "createdAt": "...", "updatedAt": "...", "deleted": false }
```

#### `POST /crm/deals` — auth: member
Required: `orgId`, `title`, `contactId`. Defaults: `value=0`, `currency='USD'`.
- `pipelineId` defaults to the org's default pipeline (auto-resolved).
- `stageId` defaults to the first `kind: 'open'` stage in that pipeline.
- Currencies: `USD`, `EUR`, `ZAR`. `orgId` is **required** — 400 if missing. Dispatches `deal.created`.

#### `GET /crm/deals/[id]` — auth: viewer
#### `PUT /crm/deals/[id]` / `PATCH /crm/deals/[id]` — auth: member
- Changing `pipelineId` requires an explicit `stageId` in the same call (else 400).
- Cross-pipeline `stageId` (stageId that does not belong to the supplied `pipelineId`) → 400.
- Stage-change dispatches `deal.stage_changed`; payload now carries `pipelineId`, `stageId`, `stageLabel`, `stageKind`, `previousStageId`, `previousStageLabel`, `previousStageKind`.
- If new stage has `kind: 'won'` → also dispatches `deal.won`; `kind: 'lost'` → `deal.lost`.
- `tryAttributeDealWon` is keyed off `stage.kind === 'won'` (not a legacy stage string).
#### `DELETE /crm/deals/[id]` — auth: admin

### CRM activities (cross-cutting)

#### `GET /crm/activities` — auth: admin
All activities across contacts/deals. Filters: `contactId`, `dealId`, `type`, `from`, `to`, `page`, `limit`.

#### `POST /crm/activities` — auth: admin
Log an activity not tied to a specific contact resource (e.g., generic meeting note).

### Quotes

#### `GET /quotes` — auth: viewer
List quotes. Filter `?orgId=X`. Supports `view=sent|received|shared`.

- `view=sent` or omitted lists quotes owned/sent by the active org.
- `view=received` lists quotes where `recipientOrgId` is the client org.
- `view=shared` lists token-claim/shared quote rows without leaking unrelated org data.
- For PiB-issued client quotes, the client portal Billing tab uses `GET /quotes?view=received`.

Sorted `createdAt desc`, limit 50.

#### `POST /quotes` — auth: member
Required: `orgId` (the client org), `lineItems: [{ description, quantity, unitPrice }]`.

Body:
```json
{
  "orgId": "org_abc",
  "lineItems": [{ "description": "Implementation", "quantity": 1, "unitPrice": 50000 }],
  "taxRate": 15,
  "currency": "ZAR",
  "notes": "...",
  "validUntil": "2026-05-31"
}
```

Auto-snapshots: `fromDetails` (from platform owner org), `clientDetails` (from client org `billingDetails`).
Auto-computes: `subtotal`, `taxAmount`, `total`. Assigns sequential `quoteNumber`.

PiB-issued quotes should keep PiB as source/issuer and the client as recipient: `orgId/sourceOrgId/issuerOrgId = pib-platform-owner`, `recipientOrgId/targetOrgId = client org`, and `companyId/sourceCompanyId` should point to the PiB platform CRM Company when available. Quote-to-invoice conversion must preserve these source/recipient and CRM fields.

Response (201): `{ id, quoteNumber }`. Dispatches `quote.created`.

#### `GET /quotes/[id]` — auth: viewer
Full quote.

#### `GET /quotes/[id]/html` — auth: viewer
Returns print-friendly quote HTML (invoice layout with the quote number) for Messages Context Dock preview.

#### `GET /quotes/[id]/pdf` — auth: viewer
Returns a PDF binary of the quote (same layout as the HTML preview).

#### `POST /quotes/[id]/send` — auth: member (sender)
Draft → sent. Emails `clientDetails.email` / `recipientEmail` with the quote PDF attached. Requires a client email. Returns `{ id, status, emailed, recipientEmail }`.

#### `PATCH /quotes/[id]` — auth: member
Update fields. Status transitions: `draft` → `sent` → `accepted` | `rejected` | `converted`.
- On `status=accepted`: dispatches `quote.accepted`
- On `status=rejected`: dispatches `quote.rejected`
- On `status=converted`: typically paired with creating an invoice from the quote

#### `DELETE /quotes/[id]` — auth: admin
Soft-delete.

### Messages quote preview handoff

When creating or preparing a quote inside Messages, emit `open_context` so the human can review the document layout in the Context Dock:

```json
{
  "id": "open-quote",
  "type": "open_context",
  "label": "Preview quote",
  "payload": { "kind": "quote", "id": "<quoteId>", "label": "<quoteNumber>" }
}
```

Messages attaches the quote and opens the side canvas with the same HTML preview used by the portal, plus **Download PDF** and **Send email** (PDF attachment) actions for drafts. Still link `/admin/quotes/[id]` (or the portal quotes workspace) for full edit/convert flows. Do not convert until the human confirms.

### AI Contact Brief

#### `GET /ai/contact-brief/[id]` — auth: admin
Generates an AI-written briefing on a contact using their activity history + company info.

Returns:
```json
{ "contactId": "contact_abc", "brief": "Markdown briefing...",
  "talkingPoints": ["..."], "recentActivity": [...], "generatedAt": "..." }
```

Use this before any outbound call or email.

### Forms (lead capture)

#### `GET /forms` — auth: viewer
List. Filters: `orgId` (required), `active`, `search`, `page`, `limit`.

#### `POST /forms` — auth: admin (slug-unique per org — duplicate slug → 409)
Create a form.

Body:
```json
{
  "orgId": "org_abc",
  "name": "Homepage Enquiry",
  "slug": "homepage-enquiry",
  "title": "Get in touch",
  "description": "...",
  "fields": [
    { "id": "name", "type": "text", "label": "Your name", "required": true },
    { "id": "email", "type": "email", "label": "Email", "required": true },
    { "id": "message", "type": "textarea", "label": "How can we help?", "required": false }
  ],
  "thankYouMessage": "Thanks — we'll be in touch.",
  "notifyEmails": ["sales@acme.com"],
  "redirectUrl": null,
  "createContact": true,
  "rateLimitPerMinute": 10,
  "active": true
}
```

`slug` must be unique per org. Supported field types: `text`, `textarea`, `email`, `phone`, `number`, `select`, `multiselect`, `checkbox`, `radio`, `date`, `file`, `hidden`.

**Optional Turnstile (Cloudflare) CAPTCHA**: include `turnstileEnabled: true` and `turnstileSiteKey: "<site_key>"` on the form. Requires `TURNSTILE_SECRET_KEY` env var. Public page embeds `<div class="cf-turnstile" data-sitekey="<siteKey>">` and the widget's hidden `cf-turnstile-response` field must be submitted with the body. Submit endpoint verifies against Cloudflare and rejects invalid tokens with 400.

Response (201): `{ id, slug }`.

#### `GET /forms/[id]` — auth: viewer
#### `PUT /forms/[id]` — auth: admin
`slug` can only change if no submissions exist yet (409 otherwise).
#### `DELETE /forms/[id]` — auth: admin

#### `POST /forms/[slug]/submit` — **public, no auth**
Query param: `?orgId=X` (required). Body is the form data keyed by `fieldId`.

#### `GET /embed/form/[publicKey]` — **public, no auth**
Embeddable public form surface for a published capture form.

Safeguards:
- Form must be `active: true`
- Honeypot field `_hp` — if populated, silent accept (returns 200 with thankYouMessage)
- Per-IP rate limit (default 10/min, configurable on form)
- Field validation (type, required, min/max, pattern)
- Optional Cloudflare Turnstile CAPTCHA — set `turnstileEnabled: true` + `turnstileSiteKey` on the form. The public widget injects `cf-turnstile-response`; the server verifies via `TURNSTILE_SECRET_KEY`

Response:
```json
{ "success": true, "data": {
    "submitted": true, "thankYou": "Thanks — we'll be in touch.", "redirectUrl": null } }
```

If `createContact: true` and `email` is valid, upserts a `Contact` (source=`form`) and links it via `contactId` on the submission. Dispatches `form.submitted` webhook.

### Attribution on public /submit

The public `/forms/[id]/submit` endpoint writes `createdByRef = formSubmissionRef(formId, formName)` on three records when triggered by an anonymous visitor:
- The `FormSubmission` doc
- The auto-created Contact (only on INSERT — existing Contact's `createdByRef` is NOT overwritten)
- A new Activity record (`type: 'note'`, `summary: 'Submitted form: <formName>'`) linked to the contact

The synthetic actor uid is `system:form-submission:<formId>` and `kind: 'system'`.

#### `GET /forms/[id]/submissions` — auth: viewer
Filters: `status` (`new`|`read`|`archived`), `from`, `to`, `page`, `limit`.

#### `GET /forms/[id]/submissions/[subId]` — auth: viewer
#### `PATCH /forms/[id]/submissions/[subId]` — auth: admin
PATCH updates `status`.

### Comments on CRM resources

#### `POST /comments`
```json
{ "orgId": "org_abc", "resourceType": "deal", "resourceId": "deal_xyz",
  "body": "Sending renewal quote tomorrow. @user:uid123 please review." }
```

Supported `resourceType` for this skill: `contact`, `deal`, `quote`, `form_submission`.

### Tasks & meetings linked to contacts/deals

See the `project-management` skill for full task and calendar APIs. Quick patterns used here:

```bash
# Task for a deal
POST /tasks
{ "orgId": "org_abc", "title": "Send proposal draft", "dueDate": "2026-04-20",
  "priority": "high", "dealId": "deal_xyz", "assignedTo": { "type": "user", "id": "uid123" } }

# Meeting with contact
POST /calendar/events
{ "orgId": "org_abc", "title": "Acme demo", "startAt": "2026-04-22T14:00:00Z",
  "endAt": "2026-04-22T15:00:00Z",
  "relatedTo": { "type": "contact", "id": "contact_abc" },
  "attendees": [{ "name": "Jane Doe", "email": "jane@acme.com", "status": "pending" }] }
```

---

## Workflow guides

### 0. Retainer / recurring client (do not open a monthly deal)

```text
Win once with a deal → move to Won → contact type=client
Ongoing months → recurring invoice schedule (billing-finance / Nora)
Upsell, expansion, or at-risk renewal → NEW deal only then
Never create 12 deals for a 12-month retainer to inflate "Won this month"
Paid invoices do NOT auto-close deals and do NOT feed wonThisMonth
```

### 1. Lead → form → contact → deal → quote → won

```bash
# Lead submits form (public)
POST /forms/homepage-enquiry/submit?orgId=org_abc
{ "name": "Jane", "email": "jane@acme.com", "message": "..." }
# → createContact:true upserts Contact, dispatches form.submitted

# Sales rep qualifies
PUT /crm/contacts/contact_abc
{ "stage": "contacted", "type": "prospect" }

# Create deal (use stageId on multi-pipeline orgs; stage aliases may still appear in older docs)
POST /crm/deals
{ "orgId": "org_abc", "contactId": "contact_abc",
  "title": "Acme - Pro Plan", "value": 12000, "currency": "ZAR", "stageId": "discovery" }

# Get AI brief before demo call
GET /ai/contact-brief/contact_abc

# Log the call
POST /crm/contacts/contact_abc/activities
{ "type": "call", "summary": "30-min demo — ready for proposal", "dealId": "deal_xyz" }

# Move deal forward
PUT /crm/deals/deal_xyz
{ "stageId": "proposal" }   # dispatches deal.stage_changed; probability follows stage unless overridden

# Create quote
POST /quotes
{ "orgId": "org_abc", "lineItems": [{ "description": "Pro Plan — annual",
  "quantity": 1, "unitPrice": 12000 }], "taxRate": 15, "currency": "ZAR" }

# Send quote externally, then mark accepted
PATCH /quotes/quote_123
{ "status": "accepted" }  # dispatches quote.accepted

# Close-won (pipeline stage kind=won → probability 100 → Overview wonThisMonth)
PUT /crm/deals/deal_xyz
{ "stageId": "won" }  # dispatches deal.stage_changed + deal.won

# Convert: create invoice / monthly recurring schedule (see billing-finance; Nora executes finance gates)
# PUT contact type to client after close-won
```

### 2. Tag and segment contacts

```bash
# Bulk tag adds via individual calls (no bulk endpoint today)
POST /crm/contacts/contact_abc/tags
{ "add": ["enterprise", "south-africa"] }

# Filter by tags
GET /crm/contacts?tags=enterprise,south-africa
```

### 3. Build a public lead-capture form

```bash
POST /forms
{ "orgId": "org_abc", "name": "Demo request", "slug": "demo-request", ... }

# Public URL to embed:
#   <form action="https://partnersinbiz.online/api/v1/forms/demo-request/submit?orgId=org_abc" method="POST">

GET /forms/form_123/submissions?status=new  # triage inbox
```

### 4. Pipeline view

Use the `platform-ops` skill's `/reports/pipeline` endpoint for `byStage` counts + values + win rate.

## Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `Name is required` / `Email is required` | Supply field |
| 400 | `Email is invalid` | Valid format |
| 400 | `Invalid stage` / `Invalid currency` | Use allowed values |
| 400 | `tags param exceeds 10` | Split into smaller batches |
| 400 | `Missing _orgId_ query param` (form submit) | Include `?orgId=X` |
| 400 | Form validation errors | Check field constraints |
| 400 | `tags filter supports up to 10 values` | Reduce segment `tags` filter array |
| 400 | `rows must be an array` / `rows must not be empty` | Check import body |
| 400 | `rows exceeds maximum of 5000` | Split import into smaller batches |
| 400 | `provider is required` / `name is required` | Supply fields on integration create |
| 400 | `config.<field> is required for <Provider>` | Supply all required provider config fields |
| 400 | `No editable fields supplied` | Send at least one editable field on PUT |
| 400 | `Invalid or missing type` (capture source) | Use `form`\|`api`\|`csv`\|`integration`\|`manual` |
| 404 | `Contact not found` / `Deal not found` | Verify ID |
| 404 | `Segment not found` / `Integration not found` / `CaptureSource not found` | Verify ID |
| 409 | `Cannot change slug after submissions exist` | Use new form or archive old |
| 422 | `<Provider> is not yet available` | Provider marked `comingSoon` |
| 422 | `A sync is already in progress` | Wait for current sync to finish |
| 422 | `Integration is paused — resume it first` | PUT `status: 'active'` then retry sync |
| 429 | Form rate limit exceeded | Retry after `Retry-After` seconds |

## Agent patterns

1. **Always send `X-Org-Id: <orgId>` header** on all Bearer contact calls — middleware reads orgId from there, not the body. For deals/quotes/forms/activities, still pass `orgId` in the body (those routes not yet migrated).
2. **Get a contact brief before calls** — `GET /ai/contact-brief/[id]` is cheap and rich.
3. **Log activities proactively** — AI should log every call/email so future briefs are accurate.
4. **Use tags for segmentation** — cheaper than custom fields and queryable with `array-contains-any`.
5. **Webhook subscriptions** — listen for `contact.created`, `deal.won`, `form.submitted` to trigger downstream flows (see `platform-ops`).
6. **Idempotency** — CRM POST routes do NOT honour `Idempotency-Key`. Do not retry a POST unless you have confirmed the prior call failed. See `## Idempotency` section for per-route details.

---

### CRM Segments (dynamic contact lists)

Segments are named, saved filter sets that resolve to a live list of matching contacts on demand. They are the right tool whenever you need to operate on a subset of contacts — bulk-enrol in a campaign, preview audience size, or hand off a list to email-outreach.

#### `GET /crm/segments?orgId=...` — auth: client
List all segments for an org. Returns segments ordered `createdAt desc`, excluding soft-deleted.

Response: array of `Segment`:
```json
{ "id": "seg_abc", "orgId": "org_xyz", "name": "Enterprise SA leads",
  "description": "...", "filters": { ... },
  "createdAt": "...", "updatedAt": "..." }
```

#### `POST /crm/segments` — auth: client
Create a segment. Required: `orgId`, `name`. `filters` is optional (empty = all contacts in org).

Body:
```json
{
  "orgId": "org_xyz",
  "name": "Enterprise SA leads",
  "description": "High-value SA prospects not yet in demo stage",
  "filters": {
    "tags": ["enterprise", "south-africa"],
    "stage": "contacted",
    "type": "prospect",
    "source": "form",
    "capturedFromIds": ["src_abc", "src_def"],
    "createdAfter": "2026-01-01T00:00:00Z"
  }
}
```

**Filter fields:**

| Field | Type | Behaviour |
|---|---|---|
| `tags` | `string[]` (max 10) | OR match — contact must have at least one of these tags (`array-contains-any`) |
| `capturedFromIds` | `string[]` (max 10) | OR match — contact was captured by one of these `CaptureSource` ids |
| `stage` | `string` | Exact match — `new`\|`contacted`\|`replied`\|`demo`\|`proposal`\|`won`\|`lost` |
| `type` | `string` | Exact match — `lead`\|`prospect`\|`client`\|`churned` |
| `source` | `string` | Exact match — `manual`\|`form`\|`import`\|`outreach` |
| `createdAfter` | ISO 8601 timestamp | Contact `createdAt >= value` |

All filters are ANDed together. The resolver always excludes deleted, unsubscribed, and bounced contacts regardless of filters.

Constraint: `tags` array-contains-any limit is 10. Return 400 if exceeded.

Response (201): `{ "id": "seg_abc" }`

#### `GET /crm/segments/[id]` — auth: client
Fetch one segment (full object including filters).

#### `PUT /crm/segments/[id]` — auth: client
Update `name`, `description`, and/or `filters`. Any field omitted is left unchanged. `name` cannot be set to empty string.

#### `DELETE /crm/segments/[id]` — auth: client
Soft-delete (`deleted: true`).

#### `POST /crm/segments/[id]/resolve` — auth: client
Execute the segment's saved filters and return matching contacts. No body required.

Response:
```json
{
  "count": 142,
  "ids": ["contact_1", "contact_2", "..."],
  "contacts": [ /* first 50 full contact docs for preview */ ]
}
```

- `count` — total matched (capped at 5000 internally; if `count == 5000` assume there may be more)
- `ids` — every matched contact id — use this to bulk-enrol contacts into a campaign
- `contacts` — first 50 full contact objects for display/preview

**Typical pattern: resolve then enrol**
```bash
# 1. Resolve the segment
POST /crm/segments/seg_abc/resolve
# → { count: 142, ids: ["contact_1", ...], contacts: [...] }

# 2. Enrol all ids into a campaign (see email-outreach skill)
POST /email-outreach/campaigns/camp_xyz/enrol
{ "contactIds": ["contact_1", "contact_2", ...] }
```

---

### CRM Integrations (third-party contact sync)

CRM integrations pull contacts from external systems (Mailchimp, HubSpot, Google Contacts, Zapier) into the PiB contact database on demand or on a cadence.

**Supported providers:**

| Provider | `provider` value | Status | Required config |
|---|---|---|---|
| Mailchimp | `mailchimp` | Live | `apiKey` (with data-centre suffix, e.g. `-us21`), `listId` (Audience ID) |
| HubSpot | `hubspot` | Live | `accessToken` (Private App token with `crm.objects.contacts.read`) |
| Google Contacts | `gmail` | Live | `refreshToken` (OAuth2 with `contacts.readonly` scope); `clientId` / `clientSecret` optional (defaults to platform client) |
| Zapier / n8n / Make | `zapier` | No integration record needed | Use a `CaptureSource` of type `api` and POST to the public capture endpoint |

Sensitive config values (`apiKey`, `accessToken`, `refreshToken`, `clientSecret`) are AES-256-GCM encrypted in Firestore and never returned in API responses. `configPreview` in the public view redacts them to `•••••<last4>`.

#### `GET /crm/integrations?orgId=...` — auth: client
List integrations for an org. Returns `PublicCrmIntegrationView[]` (config redacted).

Response:
```json
[{
  "id": "intg_abc",
  "provider": "mailchimp",
  "name": "Main audience",
  "status": "active",
  "cadenceMinutes": 60,
  "autoTags": ["mailchimp"],
  "autoCampaignIds": [],
  "lastSyncedAt": "2026-05-07T08:00:00Z",
  "lastSyncStats": { "imported": 320, "created": 12, "updated": 4, "skipped": 0, "errored": 0 },
  "lastError": "",
  "configPreview": { "apiKey": "•••••us21", "listId": "a1b2c3d4e5" }
}]
```

#### `POST /crm/integrations` — auth: client
Create an integration. Required: `orgId`, `provider`, `name`, all provider-required config fields.

Body:
```json
{
  "orgId": "org_xyz",
  "provider": "mailchimp",
  "name": "Main newsletter list",
  "config": {
    "apiKey": "abc123-us21",
    "listId": "a1b2c3d4e5"
  },
  "autoTags": ["mailchimp", "newsletter"],
  "autoCampaignIds": [],
  "cadenceMinutes": 60
}
```

- `cadenceMinutes: 0` — manual sync only (no automatic cadence)
- `autoTags` — tags applied to every contact imported through this integration
- `autoCampaignIds` — campaigns to auto-enrol new contacts on import
- Initial `status` is `pending` (changes to `active` or `error` after first sync)

Response (201): `PublicCrmIntegrationView` with `configPreview`.

#### `GET /crm/integrations/[id]` — auth: client
Fetch one integration (public view, config redacted).

#### `PUT /crm/integrations/[id]` — auth: client
Update editable fields. Supports partial update — only supplied fields change.

Editable: `name`, `config` (merged into existing, re-encrypted), `autoTags`, `autoCampaignIds`, `cadenceMinutes`, `status` (`paused`|`active` only — use to pause/resume).

Response: updated `PublicCrmIntegrationView`.

#### `DELETE /crm/integrations/[id]` — auth: client
Soft-delete.

#### `POST /crm/integrations/[id]/sync` — auth: client
Manually trigger a sync run. No body required.

**Status lifecycle during sync:**
1. Sets `status = 'syncing'`
2. Runs the provider handler (Mailchimp pulls audience members, HubSpot pulls contacts, etc.)
3. On success: `status = 'active'`, writes `lastSyncedAt` + `lastSyncStats`
4. On failure: `status = 'error'`, writes `lastError`

Cannot trigger if integration is already `syncing`, `paused`, or `disabled` (returns 422).

Response:
```json
{
  "integration": { /* updated PublicCrmIntegrationView */ },
  "ok": true,
  "stats": { "imported": 320, "created": 12, "updated": 4, "skipped": 0, "errored": 0 },
  "error": ""
}
```

**Sync dedup behaviour:** existing contacts (matched by `orgId` + `email`) have their tags merged; name, company and other fields are not overwritten. Only net-new contacts increment `capturedCount`.

---

### Capture Sources (lead source attribution)

A CaptureSource tracks where contacts come from. Every contact can carry a `capturedFromId` pointing to the source that created it, enabling attribution reporting and segmentation by source.

**Types:**

| `type` | Use case |
|---|---|
| `form` | Embeddable form widget on a client's website |
| `api` | Public POST endpoint for Zapier / n8n / Make / custom integrations |
| `csv` | Tracks a CSV import batch |
| `integration` | Mailchimp / HubSpot / Google Contacts sync |
| `manual` | Contact entered by hand in the portal |

Each source has an opaque `publicKey` (32 hex chars) used to authenticate public POSTs to `/api/public/capture/[publicKey]`. Rotating the key immediately invalidates any deployed widgets or integrations using it.

#### `GET /crm/capture-sources?orgId=...` — auth: client
List capture sources for an org. Returns sources ordered `createdAt desc`, excluding soft-deleted.

Response: array of `CaptureSource`:
```json
{
  "id": "src_abc",
  "orgId": "org_xyz",
  "name": "Homepage contact form",
  "type": "form",
  "publicKey": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
  "enabled": true,
  "autoTags": ["homepage", "inbound"],
  "autoCampaignIds": ["camp_xyz"],
  "redirectUrl": "https://acme.com/thank-you",
  "consentRequired": false,
  "capturedCount": 47,
  "lastCapturedAt": "2026-05-06T14:22:00Z",
  "createdAt": "...", "updatedAt": "..."
}
```

#### `POST /crm/capture-sources` — auth: client
Create a capture source. Required: `orgId`, `name`, `type`.

Body:
```json
{
  "orgId": "org_xyz",
  "name": "Homepage contact form",
  "type": "form",
  "autoTags": ["homepage", "inbound"],
  "autoCampaignIds": ["camp_xyz"],
  "redirectUrl": "https://acme.com/thank-you",
  "consentRequired": false
}
```

- `publicKey` is generated automatically (do not supply it)
- `enabled` defaults to `true`
- `capturedCount` starts at 0

Response (201): full `CaptureSource` including generated `publicKey`.

#### `GET /crm/capture-sources/[id]` — auth: client
Fetch one capture source.

#### `PUT /crm/capture-sources/[id]` — auth: client
Update editable fields: `name`, `enabled`, `autoTags`, `autoCampaignIds`, `redirectUrl`, `consentRequired`.

Special: pass `"rotateKey": true` to regenerate the `publicKey`. This immediately invalidates any form widgets or integrations using the old key — deploy the new key before rotating.

Response: updated `CaptureSource`.

#### `DELETE /crm/capture-sources/[id]` — auth: client
Soft-delete.

**Linking sources to contacts:** pass `capturedFromId` when creating a contact (or on import via `capturedFromId` param). The source's `capturedCount` increments automatically on new contact creates. Use `capturedFromIds` in segment filters to target all contacts from a specific source.

---

### Contact Import (bulk CSV/JSON)

#### `POST /crm/contacts/import` — auth: client

Bulk-create up to 5,000 contacts from a parsed row array. Caller is responsible for CSV parsing — send the rows as JSON.

Body:
```json
{
  "orgId": "org_xyz",
  "capturedFromId": "src_abc",
  "defaultTags": ["imported-2026-05"],
  "dryRun": false,
  "rows": [
    {
      "email": "jane@acme.com",
      "name": "Jane Doe",
      "company": "Acme Corp",
      "phone": "+27821234567",
      "tags": ["enterprise"],
      "notes": "Met at conf"
    },
    {
      "email": "bob@startup.io",
      "firstName": "Bob",
      "lastName": "Smith"
    }
  ]
}
```

**Row fields:**

| Field | Required | Notes |
|---|---|---|
| `email` | Yes | Lowercased, validated. Rows with missing/invalid email are skipped. |
| `name` | No | Used as-is if provided |
| `firstName` + `lastName` | No | Combined into `name` if `name` is absent |
| `company` | No | |
| `phone` | No | |
| `tags` | No | Merged with `defaultTags` and capture source `autoTags` |
| `notes` | No | |

**Top-level params:**

| Param | Notes |
|---|---|
| `capturedFromId` | Optional. CaptureSource id — applies its `autoTags` and bumps `capturedCount` by new creates. Must belong to the same org or is silently ignored. |
| `defaultTags` | Applied to every row, merged with per-row `tags` and source `autoTags`. |
| `dryRun` | When `true`: validates and partitions rows (create vs update) without writing. Returns `previewSample` (first 4 normalized rows). Safe to call repeatedly before committing. |

**Dedup behaviour:** contacts are matched by `orgId` + `email` (case-insensitive).
- **New email** → creates contact with `source='import'`, `type='lead'`, `stage='new'`.
- **Existing email** → merges tags only (no name/company/phone overwrite). Counted as `updated`.
- **Duplicate email within the same payload** → second occurrence is skipped with `reason: 'duplicate email in payload'`.
- Auto-campaign enrolment is intentionally skipped for imports to avoid surprise sends.

**Response:**
```json
{
  "created": 87,
  "updated": 12,
  "skipped": 3,
  "invalidRows": [
    { "index": 4, "reason": "email is invalid" },
    { "index": 9, "reason": "email is required" }
  ]
}
```

Dry-run also includes:
```json
{
  "previewSample": [
    { "index": 0, "email": "jane@acme.com", "name": "Jane Doe",
      "company": "Acme Corp", "phone": "+27821234567",
      "tags": ["enterprise", "imported-2026-05"], "notes": "Met at conf",
      "capturedFromId": "src_abc" }
  ]
}
```

**Limits:** max 5,000 rows per request. Committed in Firestore batch writes of 400 ops.

**Typical CSV import flow:**
```bash
# 1. Create a CSV capture source (once per org)
POST /crm/capture-sources
{ "orgId": "org_xyz", "name": "May 2026 conference list", "type": "csv" }
# → { "id": "src_conf_may" }

# 2. Parse CSV client-side, dry-run first
POST /crm/contacts/import
{ "orgId": "org_xyz", "capturedFromId": "src_conf_may",
  "defaultTags": ["conference-2026"], "dryRun": true,
  "rows": [ { "email": "...", "name": "..." } ] }
# → review invalidRows + previewSample

# 3. Commit
POST /crm/contacts/import
{ "orgId": "org_xyz", "capturedFromId": "src_conf_may",
  "defaultTags": ["conference-2026"], "dryRun": false,
  "rows": [ ... ] }
# → { "created": 210, "updated": 8, "skipped": 2, "invalidRows": [...] }
```

## Ads attribution (cross-ref)

When a deal closes-won, the system can call `POST /api/v1/ads/conversions/track`
to feed Meta CAPI. This requires:
- A pixel config configured under `/admin/org/<slug>/ads/pixel-config`
- The deal contact's email + phone hashed and posted as the `user.email` /
  `user.phone` fields in the event payload (server hashes — DO NOT pre-hash
  in skill calls)
- An `event_id` matching the browser pixel's eventID for dedupe

---

## Companies (A1 — first-class entity)

Companies are now a first-class CRM entity. Every `Contact`, `Deal`, `Quote`, and `Activity` can carry `companyId` and be linked to a `Company` record.

### Company field reference

| Field | Type | Notes |
|---|---|---|
| `id` | string | Firestore doc ID |
| `orgId` | string | Tenant scope — always enforced |
| `name` | string | Required, max 200 chars |
| `domain` | string? | e.g. `acme.com` — lowercased on write, used for fuzzy matching |
| `website` | string? | Full URL accepted |
| `industry` | string? | Free-form |
| `size` | `'1-10'|'11-50'|'51-200'|'201-1000'|'1000+'`? | |
| `employeeCount` | number? | |
| `annualRevenue` | number? | |
| `currency` | Currency? | For annualRevenue |
| `tier` | `'enterprise'|'mid-market'|'smb'`? | |
| `lifecycleStage` | `'lead'|'prospect'|'customer'|'churned'`? | |
| `tags` | string[] | Default `[]`, max 30 |
| `notes` | string | Default `''`, max 10 000 chars |
| `phone` | string? | |
| `address` | CompanyAddress? | `{ street, city, state, country, postalCode, label }` |
| `secondaryAddresses` | CompanyAddress[]? | |
| `socialProfiles` | SocialProfiles? | `{ linkedin, twitter, facebook, instagram }` |
| `logoUrl` | string? | Firebase Storage path OR external URL |
| `parentCompanyId` | string? | Same-org only; cycle-detection enforced (max 10 levels) |
| `linkedOrgId` | string? | **Read-only / system-managed.** Target org this sender-owned company represents. Rejected from POST/PUT/PATCH bodies — set only by an accepted partner invite or the platform-owner sync. See Partner Links below. |
| `accountManagerUid` | string? | Must be org member |
| `accountManagerRef` | MemberRef? | Snapshot at write |
| `healthScore` | number? | 0-100, nullable until A6 automation |
| `customFields` | Record\<string, unknown\>? | Unvalidated until A2 |
| `ownerUid` | string? | |
| `ownerRef` | MemberRef? | |
| `createdBy` | string? | |
| `createdByRef` | MemberRef? | |
| `updatedBy` | string? | |
| `updatedByRef` | MemberRef? | |
| `createdAt` | Timestamp\|null | |
| `updatedAt` | Timestamp\|null | |
| `deleted` | boolean? | `true` on soft-delete |

### Hybrid migration model

`Contact.company` (plain string) is preserved. New fields are additive:

| Contact reads | Meaning |
|---|---|
| `companyId` set + `companyName` cached | Use cache (saves a Firestore read) |
| `companyId` set, no cache | Look up `company.name` for current state |
| `companyId` unset + `company` set | Use `company` string as display label (B2C fallback) |
| both unset | "No company" |

When linking a contact to a company, write both `companyId` + `companyName`. On company rename, best-effort cache-refresh updates `companyName` on all linked records (in-band for ≤30, background for more). On unlink, clear `companyId` + `companyName`, preserve `company` string.

Platform-owner CRM sync adds one PiB Company per client org (`linkedOrgId`) and one PiB Contact per active real client member (`linkedUserId`, `linkedOrgId`, `companyId`). Internal `@partnersinbiz.online` staff are not mirrored as client contacts when backfilling client organizations.

### Company endpoints

#### `GET /crm/companies` — auth: viewer
List companies with filters + pagination.

Query params:
- `search` — substring on `name`/`domain`/`website` (case-insensitive in-memory)
- `industry` — exact
- `size` — `1-10`|`11-50`|`51-200`|`201-1000`|`1000+`
- `tier` — `enterprise`|`mid-market`|`smb`
- `lifecycleStage` — `lead`|`prospect`|`customer`|`churned`
- `tags` — comma-separated (array-contains-any, max 10)
- `accountManagerUid` — exact
- `hasOpenDeals` — bool (`true` = companies with at least one open deal)
- `limit` — default 50, max 200
- `cursor` — Firestore cursor (opaque) for next page
- `orderBy` — `createdAt-desc` (default) | `name-asc` | `updatedAt-desc`

Response:
```json
{ "success": true, "data": { "companies": [ { "id": "co_abc", "orgId": "org_xyz", "name": "Acme Corp", "domain": "acme.com", ... } ] } }
```

#### `POST /crm/companies` — auth: member
Create a company. Required: `name`.

Body: any subset of Company fields (except `id`, `orgId`, `createdAt`, `updatedAt`). `orgId` is resolved from auth middleware.

Response (201): `{ id: "co_abc", ...fields }`

#### `GET /crm/companies/[id]` — auth: viewer
Full company record.

#### `PUT /crm/companies/[id]` — auth: member
Full replace. Empty body → 400.

#### `PATCH /crm/companies/[id]` — auth: member
Partial update. Empty body → 400.

#### `DELETE /crm/companies/[id]` — auth: admin
Soft-delete (`deleted: true`). Triggers cascade soft-clear of `companyId` + `companyName` on all linked contacts, deals, quotes, and activities within the same org (best-effort, 30-record batches). Does NOT delete linked records.

Response: `{ id: "co_abc" }`

#### `POST /crm/companies/bulk` — auth: member
Bulk-update multiple companies.

Body:
```json
{ "ids": ["co_1", "co_2"], "patch": { "accountManagerUid": "uid123", "tier": "enterprise" } }
```

Allowed `patch` fields: `accountManagerUid`, `ownerUid`, `tags` (replace), `tier`, `lifecycleStage`, `industry`, `size`. Others → 400.

#### `POST /crm/companies/[id]/upload-logo` — auth: member
Upload a company logo. `Content-Type: multipart/form-data`, field `logo`. Max 5 MB. Allowed types: `image/png`, `image/jpeg`, `image/webp`, `image/svg+xml`.

Response: `{ logoUrl: "https://storage.googleapis.com/..." }`

#### `POST /crm/companies/migrate-from-contacts` — auth: admin
Migration tool: group existing plain-string `contact.company` values into real Company records.

**Preview mode (default):**
```json
{ "mode": "preview" }
```
Response: list of normalized groups with `normalizedKey`, `rawValues`, `contactIds`, `suggestedCompanyName`, `existingCompanyId`.

**Apply mode:**
```json
{ "mode": "apply", "selections": [ { "normalizedKey": "acme corp", "suggestedCompanyName": "Acme Corp", "contactIds": ["c1","c2"], "existingCompanyId": null } ] }
```
Per selection: creates company if `existingCompanyId === null`, then batch-links contacts. Returns per-row `created`/`linked`/`failed`. Idempotent.

#### `GET /crm/companies/[id]/contacts` — auth: viewer
Contacts linked to this company via `companyId`. Query: `limit` (default 50, max 200). Sorted `updatedAt desc`.

#### `GET /crm/companies/[id]/deals` — auth: viewer
Deals linked to this company. Query: `limit`. Sorted `updatedAt desc`. Excludes soft-deleted.

#### `GET /crm/companies/[id]/quotes` — auth: viewer
Quotes linked to this company. Query: `limit`. Sorted `updatedAt desc`.

#### `GET /crm/companies/[id]/invoices` — auth: viewer
Invoices linked to this company. Reads `companyId/sourceCompanyId` first and falls back to the company `linkedOrgId` against `recipientOrgId` / `targetOrgId` / compatible legacy org fields for PiB-owned resources.

#### `GET /crm/companies/[id]/activities` — auth: viewer
Activity timeline for this company. Query: `limit` (default 50, max 200). Sorted `createdAt desc`.

### Cascade on DELETE

`DELETE /crm/companies/[id]` soft-clears `companyId` + `companyName` on all 4 collections (`contacts`, `deals`, `quotes`, `activities`) within the same org. Uses 30-record Firestore batch chunks. Best-effort wrapped in try/catch — partial success is logged but does NOT block the delete response.

---

## Cross-entity companyId field notes

### Contact

New fields (additive, W1-A):
- `companyId?: string` — link to a Company record (same org)
- `companyName?: string` — denormalized cache of `company.name` at link time
- `linkedUserId?: string` — **read-only / system-managed.** User account represented by this sender-owned contact after a claim, partner-link accept, or platform CRM sync. Rejected from request bodies.
- `linkedOrgId?: string` — **read-only / system-managed.** Organization represented by this contact's company relationship. Rejected from request bodies.

Hybrid: `company: string` (original plain-text field) is preserved unchanged. UI falls back to `company` when `companyId` is unset.

POST and PATCH: supply `companyId` to link. If valid, the route writes both `companyId` + `companyName` from the Company record.

### Deal

New fields (additive, W1-A):
- `companyId?: string`
- `companyName?: string`

Auto-derive: POST with `contactId` → if contact has `companyId`, deal inherits it (best-effort, wrapped in try/catch). PATCH with `contactId` change → repopulates `companyId` + `companyName` from new contact. PATCH with explicit `companyId` → validated + written directly (wins over contact-derived value in same PATCH).

### Quote

Same shape and auto-derive rules as Deal. Webhook payloads (`quote.created`, `quote.accepted`, `quote.rejected`) include `companyId` + `companyName` when set.

### Activity

New field (additive, W1-A):
- `companyId?: string` — no `companyName` cache (activities only carry companyId)

Auto-derive: POST with `contactId` → if contact has `companyId`, activity inherits it (best-effort). POST with explicit `companyId` → validated against org scope (returns 400 if invalid/cross-tenant).

---

## Custom Fields (A2 — per-workspace typed fields)

Per-workspace, per-resource (contact / deal / company) typed field definitions. Validation runs on every CRM write whose body includes `customFields`. Values land in `Contact.customFields` / `Deal.customFields` / `Company.customFields` (`Record<string, unknown>`).

### Field types (12)

`text` · `longtext` · `number` · `currency` (`{amount, currency}`) · `date` (YYYY-MM-DD) · `datetime` (ISO) · `dropdown` · `multi_select` · `checkbox` · `url` · `email` · `phone`

### Endpoints

| Method | Path | Role |
|---|---|---|
| GET | `/api/v1/crm/custom-fields?resource=contact\|deal\|company` | viewer |
| POST | `/api/v1/crm/custom-fields` | admin |
| GET | `/api/v1/crm/custom-fields/[id]` | viewer |
| PUT | `/api/v1/crm/custom-fields/[id]` | admin |
| PATCH | `/api/v1/crm/custom-fields/[id]` | admin |
| DELETE | `/api/v1/crm/custom-fields/[id]` | admin (soft) |
| POST | `/api/v1/crm/custom-fields/reorder` | admin |

### Constraints

- `key` immutable after create (must match `^[a-z][a-z0-9_]{0,39}$`)
- `type` immutable after create (would corrupt stored values across existing records)
- `resource` immutable
- dropdown / multi_select require non-empty `options[]` with unique `value`
- Per-type optional constraints: text/longtext (`minLength` / `maxLength`), number/currency (`min` / `max`), currency (`currencyCode`)

### Validation contract

When `contacts`, `deals`, or `companies` receive a POST/PATCH/PUT whose body contains `customFields`, the route fetches the workspace's definitions for the resource and runs `validateCustomFields`. On failure → 400 with message `Custom field validation failed: <key>: <message>; <key>: <message>; ...`. Wrapped in best-effort try/catch around the LOOKUP (not the validation) — Firestore outage must not block core CRM writes.

Required fields → empty / null / undefined / empty array all return an error. Orphan keys (values present but no matching definition) are silently ignored (legacy support) and rendered with a "(legacy)" hint in the UI's read view.

### Cross-entity coverage

- **Contact**, **Deal**, **Company** carry `customFields?` and run validation on writes
- **Activity**, **Quote** custom-field validation deferred to a future A2-extension

### UI

- Admin settings page: `/portal/settings/custom-fields` — 3 resource tabs, add/edit/delete/reorder
- Detail pages mount `<CustomFieldsSection>` from `components/crm/` in both read and edit modes
- `CompanyEditDrawer` accepts a `customFieldDefinitions?` prop; when populated, the section appears between Relationships and Notes

---

## Pipelines (A3 — multi-pipeline support)

> **Breaking change — A3 strict cutover:** `Deal.stage: DealStage` has been **removed**. Deals now carry `pipelineId: string` + `stageId: string`. Any external integration that reads `deal.stage` must be updated before deploying. The one-shot migration script must be run BEFORE the A3 deploy or all deal writes will return 400.

### Pipeline entity field reference

| Field | Type | Notes |
|---|---|---|
| `id` | string | Firestore doc ID |
| `orgId` | string | Tenant scope — always enforced |
| `name` | string | Required |
| `description` | string? | Optional |
| `stages` | PipelineStage[] | Min 3 stages; exactly 1 `won` + 1 `lost` required |
| `isDefault` | boolean | One pipeline per org is default; atomic swap via `set-default` |
| `archived` | boolean | Archived pipelines are hidden from normal views |
| `attribution` | object? | Internal tracking metadata |

### PipelineStage field reference

| Field | Type | Notes |
|---|---|---|
| `id` | string | Must match `^[a-z][a-z0-9_]{0,39}$`; immutable after create |
| `label` | string | Display name |
| `kind` | `'open'\|'won'\|'lost'` | Immutable after create; drives attribution + webhooks |
| `order` | number | Display sort order (ascending) |
| `probability` | number | 0–100; used for weighted pipeline value |
| `color` | string? | Hex colour for kanban column |

### Validation rules

- `stages` must have length ≥ 3
- Exactly **1** stage with `kind: 'won'` and **1** stage with `kind: 'lost'` required
- Stage `id` values must be unique within the pipeline
- Stage `kind` and `id` are immutable after creation (would corrupt existing deals)

### Endpoints

| Method | Path | Min role | Notes |
|---|---|---|---|
| GET | `/api/v1/crm/pipelines?archived=false` | viewer | Lists pipelines; pass `?archived=true` to include archived |
| POST | `/api/v1/crm/pipelines` | admin | Creates a pipeline |
| GET | `/api/v1/crm/pipelines/[id]` | viewer | Full pipeline with stages |
| PUT | `/api/v1/crm/pipelines/[id]` | admin | Full replace |
| PATCH | `/api/v1/crm/pipelines/[id]` | admin | Partial update |
| DELETE | `/api/v1/crm/pipelines/[id]` | admin | Soft-delete; returns 400 if live deals are attached |
| POST | `/api/v1/crm/pipelines/[id]/set-default` | admin | Atomically marks this pipeline as default (clears old default) |
| GET | `/api/v1/crm/pipelines/default` | viewer | Returns the org's default pipeline; bootstraps a "Sales" pipeline if none exists for `member+` callers |

### Deal POST/PATCH contract

- **POST** — `pipelineId` defaults to org's default pipeline; `stageId` defaults to first `kind: 'open'` stage in that pipeline.
- **PATCH** — changing `pipelineId` requires an explicit `stageId` in the same call (else 400). A `stageId` that does not belong to the supplied `pipelineId` is rejected with 400.
- Stage-change webhook payload now carries: `pipelineId`, `stageId`, `stageLabel`, `stageKind`, `previousStageId`, `previousStageLabel`, `previousStageKind`.
- `tryAttributeDealWon` is keyed off `stage.kind === 'won'` — **not** a legacy stage string.

### Migration

**One-shot script:** `scripts/crm-migrate-multi-pipeline.ts`

- Idempotent — safe to run multiple times
- Flags: `--dry-run` (preview changes) + `--commit` (write to Firestore)
- Creates a default "Sales" pipeline per org
- Populates `pipelineId` + `stageId` on all existing deals from the legacy `stage` string
- Drops the legacy `stage` field

**This script must be run BEFORE deploying A3.** Deploying without migrating means all deal writes return 400.

### UI

- Admin settings page: `/portal/settings/pipelines` — create, edit, reorder, archive, set-default
- Kanban uses `<PipelineSelector>` to switch between pipelines

---

## Scoring (A4 — contact lead scoring)

Formula-based, ICP-match, and optional AI scoring for every contact. Scores are stored directly on the `Contact` document and recomputed on demand or nightly via cron.

### Contact fields added (additive)

| Field | Type | Notes |
|---|---|---|
| `leadScore` | `number?` | 0-100. Weighted sum of signal weights (email opens, clicks, replies, etc.) |
| `icpScore` | `number?` | 0-100. How closely the contact's company matches the org's ICP profile |
| `aiLeadScore` | `number?` | 0-100. LLM-based score via AI Gateway; only set when `aiEnabled: true` |
| `scoreUpdatedAt` | `Timestamp?` | When scores were last computed |
| `scoreSignals` | `Record<string, number>?` | Per-signal contribution map used to explain the score |

### Key types

```ts
interface ScoringConfig {
  icp: IcpProfile
  leadWeights: LeadSignalsWeights
  aiEnabled: boolean        // master AI toggle (default false)
  aiModel?: string          // default 'gpt-4o-mini'
  aiCacheHours?: number     // default 24
}

interface IcpProfile {
  industries?: string[]
  sizes?: CompanySize[]     // '1-10' | '11-50' | '51-200' | '201-1000' | '1000+'
  tiers?: CompanyTier[]     // 'enterprise' | 'mid-market' | 'smb'
  regions?: { country?: string; state?: string }[]
  minEmployeeCount?: number
  maxEmployeeCount?: number
  minAnnualRevenue?: number
  maxAnnualRevenue?: number
}

interface LeadSignalsWeights {
  emailOpens?: number         // default 2
  emailClicks?: number        // default 5
  emailReplies?: number       // default 15
  sequenceCompleted?: number  // default 10
  recentContact?: number      // default 10
  formSubmission?: number     // default 8
}
```

### Endpoints

#### `GET /crm/scoring/config` — auth: viewer
Returns the org's scoring configuration, bootstrapping defaults if absent.

Response: `{ config: ScoringConfig }`

#### `PUT /crm/scoring/config` — auth: admin
Update ICP profile, lead signal weights, and/or the AI toggle.

Body (all fields optional):
```json
{
  "icp": {
    "industries": ["SaaS", "Fintech"],
    "sizes": ["11-50", "51-200"],
    "tiers": ["smb", "mid-market"]
  },
  "leadWeights": {
    "emailReplies": 20,
    "emailClicks": 8
  },
  "aiEnabled": false
}
```

Response: `{ config: ScoringConfig }` (updated)

#### `POST /crm/contacts/[id]/recompute-score` — auth: admin
Manually recompute all scores for one contact. AI scoring runs unless `includeAi: false` or `aiEnabled` is off.

Body:
```json
{ "includeAi": true }
```

Response: `{ update: ScoreUpdate }` — includes the new `leadScore`, `icpScore`, `aiLeadScore`, and `scoreSignals`.

#### `POST /crm/scoring/recompute-all` — auth: admin
Bulk recompute scores across all org contacts. Use after changing the scoring config.

Body:
```json
{ "includeAi": false, "limit": 500 }
```

- `limit` — max 500 contacts per call. Paginate if org has more.
- `includeAi` — default `true`; set `false` to skip AI scoring on the bulk run.

Response:
```json
{ "processed": 312, "succeeded": 310, "failed": 2, "errors": ["contact_abc: ..."] }
```

> The nightly cron `GET /crm/cron/recompute-scores` is internal (system/CRON_SECRET). It runs at 02:00 UTC and processes all orgs. Do not call it from skill code.

---

## A5 — Products & Deal Extensions

### Product Catalog endpoints
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/v1/crm/products` | member | List active products |
| POST | `/api/v1/crm/products` | admin | Create product |
| PUT | `/api/v1/crm/products/[id]` | admin | Update product |
| DELETE | `/api/v1/crm/products/[id]` | admin | Soft-delete |

### Deal extended fields (A5)
- `probability?: number` — 0–100; auto-set from `stage.probability` when stageId changes; overridable
- `lostReason?: string` — freetext; only surfaced/persisted on stages whose name contains "lost"
- `lineItems?: DealLineItem[]` — snapshot array; each item: `{ productId?, name, qty, unitPrice, discount?, total, currency }`

Deal line item normalization is route-enforced in `lib/crm/deals.ts`:
- `name` is required and trimmed.
- `qty` and `unitPrice` must be finite numbers >= 0.
- `discount` is optional percentage 0–100.
- `total` is recalculated as `qty * unitPrice * (1 - discount/100)` and rounded to cents.
- `currency` must be `USD`, `EUR`, or `ZAR`; invalid/missing values fall back to the deal currency.
- Request-controlled `id`, `orgId`, audit fields, and `deleted` are stripped before Firestore writes.

Do not send quote-style `{ quantity, amount }` objects to deals. Quotes use `{ description, quantity, unitPrice, amount }`; deal line items use `{ name, qty, unitPrice, discount?, total, currency }`, and quote pre-fill maps deal `qty` to quote `quantity`.

### Quote pre-fill
- `POST /api/v1/quotes` accepts optional `dealId` — pre-populates lineItems from the deal

---

## A6 — Lifecycle Automation Triggers

### Automation Rules endpoints
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/v1/crm/automations` | member | List workspace automation rules |
| POST | `/api/v1/crm/automations` | admin | Create rule |
| PUT | `/api/v1/crm/automations/[id]` | admin | Update rule |
| DELETE | `/api/v1/crm/automations/[id]` | admin | Soft-delete rule |

### Cron
- `GET /api/v1/crm/cron/process-automations` — Bearer CRON_SECRET, runs every 5 min via Vercel cron. Processes `pending_automations` where `scheduledAt ≤ now && status === 'pending'`. Batch of 100, 55s budget.

### AutomationRule fields
- `trigger.event`: `'deal.created' | 'deal.stage_changed' | 'deal.won' | 'deal.lost' | 'contact.created' | 'contact.lifecycle_changed'`
- `trigger.toStageId?`: filter — only fire when deal moves to this specific stage
- `trigger.pipelineId?`: filter — only fire for this pipeline
- `delayMinutes?`: 0 or absent = immediate; >0 = writes PendingAutomation doc, cron executes later
- `actions[]`: one or more of `send_email | send_notification | assign_owner | dispatch_webhook`
- `enabled: boolean`: toggle without deleting

### Trigger wiring
Events fire automatically after successful CRM writes:
- `deal.created` — POST /crm/deals
- `deal.stage_changed` + `deal.won` / `deal.lost` — PUT /crm/deals/[id] on stage change
- `contact.created` — POST /crm/contacts
- `contact.lifecycle_changed` — PUT /crm/contacts/[id] when `type` field changes

All trigger calls are best-effort (dynamic import + try/catch) — automation failures never block the primary write.

### Key patterns
- `fireTrigger` always wrapped in try/catch — never throws to caller
- Executor: each action individually try/caught — one failure doesn't abort others
- Dynamic import in routes (`await import('@/lib/automations/trigger')`) avoids circular deps and keeps existing tests green
- Time-delayed actions: cron fires every 5min, processes `pending_automations` collection

---

## B-phase — CRM UI Completeness

### New endpoints
| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/v1/crm/dashboard` | member | Pipeline metrics: open deals, weighted pipeline, won/lost this month, top deals, recent activities |

### Extended endpoints
- `POST /api/v1/crm/contacts/bulk` — now accepts `patch: { delete: true }` for soft-bulk-delete (cannot combine with other patch fields)
- `GET /api/v1/crm/deals` — now accepts `?search=` param (post-filter on title)
- `POST /api/v1/crm/activities` — now accepts `occurredAt` ISO string (optional; defaults to server timestamp)

### Dashboard response shape
```json
{
  "openDealsCount": 12,
  "openDealsValue": 450000,
  "weightedPipelineValue": 225000,
  "wonThisMonth": { "count": 3, "value": 95000 },
  "lostThisMonth": { "count": 1 },
  "recentActivities": [...],
  "topOpenDeals": [...]
}
```

### UI additions (B-phase)
- **CrmSearchBar** — debounced cross-entity search (contacts + companies + deals), wired into portal sidebar
- **Contact detail** — activity timeline with icons + actor names + load-more; log-activity quick actions (Call/Email/Note); + New deal button in ContactDealsPanel
- **Contacts list** — bulk delete action added (confirms before executing)
- **Portal dashboard** — Pipeline section with 4 metric cards + activity feed + top deals table
- **Deals page** — Forecast tab with probability-weighted table, inline probability editor, relative close-date

### Key patterns
- Activity POST field: `summary` (required), not `notes`
- Bulk delete: `{ ids, patch: { delete: true } }` — exclusive, cannot mix with other patch ops
- Dashboard fetch: silent-fail — automation failure never breaks the parent page
- Probability inline edit: optimistic update + best-effort PUT

---

## Role matrix

| Resource | viewer (GET) | member (write) | admin (delete/bulk-admin) |
|---|---|---|---|
| Contacts | GET list/detail/activities/tags | POST, PUT, DELETE (if permitted) | DELETE always |
| Deals | GET list/detail | POST, PUT | DELETE |
| Quotes | GET list/detail | POST, PATCH | DELETE |
| Activities | GET list | POST | — |
| Forms | GET list/detail/submissions | — | POST, PUT, DELETE |
| Segments | GET, resolve | POST, PUT | DELETE |
| Integrations | GET list/detail | — | POST, PUT, DELETE, sync |
| Capture sources | GET list/detail | — | POST, PUT, DELETE |
| **Companies** | **GET list/detail/contacts/deals/quotes/activities** | **POST, PUT, PATCH, bulk, upload-logo** | **DELETE, migrate-from-contacts** |
| **Custom Fields** | **GET list/detail** | **—** | **POST, PUT, PATCH, DELETE, reorder** |
| **Pipelines** | **GET list/detail/default** | **—** | **POST, PUT, PATCH, DELETE, set-default** |
| **Scoring config** | **GET config** | **trigger recompute (single contact)** | **PUT config, recompute-all** |

See the Ads sub-project 1 design spec for full payload shape.

---

## C-phase — Email Sequences, AI Compose, Deduplication & Smart Suggestions

### C1 — Email Sequences

Sequences are multi-step drip campaigns. Contacts are enrolled per-sequence; the `process-sequences` cron sends due steps every 5 minutes.

#### Sequence endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/v1/crm/sequences` | member | List sequences for org |
| POST | `/api/v1/crm/sequences` | admin | Create sequence |
| GET | `/api/v1/crm/sequences/[id]` | member | Fetch one sequence |
| PUT | `/api/v1/crm/sequences/[id]` | admin | Update sequence |
| DELETE | `/api/v1/crm/sequences/[id]` | admin | Soft-delete |

Sequence body:
```json
{
  "orgId": "org_xyz",
  "name": "Onboarding drip",
  "steps": [
    { "delayDays": 0, "subject": "Welcome!", "body": "Hi {{name}}, ..." },
    { "delayDays": 3, "subject": "Checking in", "body": "..." },
    { "delayDays": 7, "subject": "Tips for success", "body": "..." }
  ]
}
```

#### Enrollment endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/v1/crm/sequences/[id]/enrollments` | member | List enrollments |
| POST | `/api/v1/crm/sequences/[id]/enrollments` | member | Enroll contact(s) |
| DELETE | `/api/v1/crm/sequences/[id]/enrollments/[enrollmentId]` | member | Unenroll |

Enrollment body: `{ "contactId": "contact_abc" }`

#### Cron

`GET /api/v1/crm/cron/process-sequences` — Bearer CRON_SECRET, runs every 5 min via Vercel cron. Processes pending sequence steps where `scheduledAt ≤ now`. Sends email via platform mailer, advances enrollment to next step or marks complete.

Activity logged on send: `type: 'sequence_enrolled'` or `type: 'sequence_completed'` on final step.

---

### C3 — AI Email Compose

Generate a personalised email draft for a contact using LLM.

#### `POST /api/v1/crm/ai/compose-email` — auth: member

Generates a CRM email draft for a contact. For sending from a **connected Gmail/SMTP mailbox**, prefer the operational mailbox flow in `platform-ops`:
`GET /agent/email/accounts` → draft via `/agent/email/drafts` → echo `open_context` uiActions so Messages opens the email side canvas for human Approve & send.

Body:
```json
{
  "contactId": "contact_abc",
  "purpose": "follow_up_after_demo",
  "tone": "professional"
}
```

- `purpose`: free string or well-known values — `follow_up_after_demo`, `send_proposal`, `check_in`, `re_engage`
- `tone`: `professional` | `friendly` | `formal` | `casual`

Response:
```json
{
  "subject": "Following up on our call",
  "body": "Hi Jane, ..."
}
```

The route fetches the contact + recent activities to ground the draft. Output is a suggestion — the human reviews and sends via their email client or sequence step.

---

### C4 — Duplicate Detection & Merge

#### `GET /api/v1/crm/contacts/duplicates` — auth: member

Returns groups of suspected duplicate contacts (matched by fuzzy email + name).

Response:
```json
{
  "groups": [
    {
      "contacts": [
        { "id": "contact_1", "name": "Jane Doe", "email": "jane@acme.com" },
        { "id": "contact_2", "name": "Jane Doe", "email": "jane@acme.com " }
      ],
      "reason": "email_match"
    }
  ]
}
```

#### `POST /api/v1/crm/contacts/merge` — auth: admin

Merges two contacts. The winner keeps all its own fields; the loser's tags, activities, deals, and form submissions are re-linked to the winner. Loser is soft-deleted after merge.

Body:
```json
{ "winnerId": "contact_1", "loserId": "contact_2" }
```

Response: `{ "id": "contact_1" }` (winner id).

---

### C5 — Smart Suggestions

Rule-based next-action suggestions for a contact. No LLM — deterministic logic based on activity recency, stage, and deal state.

#### `GET /api/v1/crm/contacts/[id]/suggestions` — auth: member

Response:
```json
{
  "suggestions": [
    { "type": "follow_up", "reason": "No contact in 14 days", "priority": "high" },
    { "type": "send_proposal", "reason": "Deal in proposal stage with no quote linked", "priority": "medium" }
  ]
}
```

Use to surface a prioritised to-do list in the contact detail panel. No side-effects — read-only.

---

### C6 — Sequence Enrollment Automation Action

The `enroll_in_sequence` action type is available in automation rules (A6). When a trigger fires, it automatically enrolls the contact into a named sequence.

Automation rule body with sequence action:
```json
{
  "trigger": { "event": "contact.created" },
  "actions": [
    {
      "type": "enroll_in_sequence",
      "sequenceId": "seq_onboarding_abc"
    }
  ]
}
```

This pairs naturally with the `contact.created` and `contact.lifecycle_changed` trigger events. The cron (`process-sequences`) handles step delivery from that point forward.

**Role matrix additions (C-phase)**

| Resource | viewer | member | admin |
|---|---|---|---|
| Sequences | GET list/detail | — | POST, PUT, DELETE |
| Enrollments | GET list | POST (enroll) | DELETE (unenroll) |
| AI compose | — | POST | — |
| Duplicates | — | GET duplicates | POST merge |
| Suggestions | — | GET suggestions | — |
