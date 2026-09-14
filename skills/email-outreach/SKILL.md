---
name: email-outreach
description: >
  Complete world-class email + SMS marketing platform — transactional + marketing emails; drip sequences
  with branching, goal-exit, and wait-until conditions; broadcasts/newsletters; visual block-based templates
  with conditional content + reusable snippets + AMP for Email; per-org sending domains with DKIM;
  behavioral segmentation + lead-capture forms with double-opt-in + popup/exit-intent/multi-step widgets;
  spam protection (Cloudflare Turnstile + honeypot + disposable-email blocking + rate limiting);
  preferences center with topic-level opt-in/out + frequency capping; AI-generated emails, subject lines,
  sequences, newsletters, winbacks, rewrites; A/B testing with split + winner-only modes and statistical
  significance; reply tracking via Resend Inbound Routes (auto-pause on reply); send-time optimization
  (timezone-aware, preferred-day + preferred-hour in recipient's local clock); pre-send preflight validation
  (broken links, accessibility, deliverability); image upload + brand kit; suppression list with hard/soft
  bounce categorization; List-Unsubscribe + List-Unsubscribe-Post one-click compliance (RFC 8058);
  webhook signature verification (svix); SMS via Twilio with multi-channel sequences; click-tracked short
  links; analytics dashboard with cohort retention, revenue attribution, click heatmaps, send-time matrix,
  industry benchmark comparison, engagement score. Uses Resend + Twilio + Vercel AI Gateway. Trigger on:
  "send email/SMS", "draft email/SMS", "email/text a contact", "schedule", "email queue",
  "create sequence", "drip campaign", "nurture sequence", "welcome series", "enroll contact",
  "broadcast", "newsletter", "blast", "template", "visual builder", "block editor", "merge fields",
  "segment", "behavioral segment", "audience", "engagement", "lead capture", "newsletter signup",
  "popup form", "exit intent", "multi-step form", "subscribe form", "double opt-in",
  "campaign", "launch campaign", "bulk email", "sending domain", "verify domain", "DNS",
  "track link", "short URL", "click stats", "AI email", "AI subject lines", "rewrite",
  "A/B test", "split test", "subject test", "winner", "statistical significance",
  "analytics", "cohort", "revenue attribution", "click heatmap", "best send time", "benchmarks",
  "engagement score", "open rate", "click rate", "bounce rate", "complaints", "unsubscribe",
  "suppression", "preferences", "frequency cap", "deliverability", "reply", "auto-pause", "out of office",
  "send time optimization", "timezone", "preflight", "validate email", "brand kit", "image upload",
  "AMP for Email", "carousel", "accordion", "live data", "dark mode", "Twilio", "SMS",
  "STOP", "multi-channel", "Turnstile", "captcha", "honeypot", "disposable email", "rate limit",
  "List-Unsubscribe", "spam protection", "svix". If in doubt, trigger.
---

# Email Outreach — Partners in Biz Platform API

A complete email marketing system. Eight layers:

1. **Sending** — transactional + drip + broadcast, all through Resend
2. **Templates** — visual block-based builder + starter template library
3. **Sequences** — multi-step drip with delays and variants
4. **Broadcasts** — one-time blasts to segments/lists with optional A/B testing
5. **Audiences** — segments + tags + lead capture forms with double-opt-in
6. **Domains** — per-org sender verification through Resend
7. **AI** — generate emails, sequences, subject variants, and rewrites
8. **Analytics** — per-org / per-broadcast / per-sequence / per-contact dashboards

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Connected mailbox vs marketing email (mandatory)

This skill covers **marketing/ESP** email (broadcasts, sequences, Resend). Operational Gmail/SMTP for a person is different:

1. Check the Messages `[Mailbox connections]` prompt block first.
2. If connected, use `GET /api/v1/agent/email/accounts` and `GET /api/v1/agent/email/messages?summarize=true` (platform-ops / agent-email toolset) before asking the user to paste emails.
3. Draft personal 1:1 replies via `POST /api/v1/agent/email/drafts` or `/replies`, then echo `uiActions`/`contextRef` (`open_context`) so Messages opens the email side canvas for human **Approve & send**.
4. Do not use marketing broadcast/sequence APIs for personal inbox triage.

## Base URL & Authentication

```
https://partnersinbiz.online/api/v1
```

```
Authorization: Bearer <AI_API_KEY>
```

Prefer the user-delegation Bearer token (`pib_dlg_…`) or a device-login / personal token from `pib-skills login` (see `system-auth`). `AI_API_KEY` is for cron/system jobs only. On 403, print the API error and stop — do not retry with a god-key.

CRM-scoped endpoints also accept scoped per-agent API keys (`pib_...`) created in platform API-key management. Pass `Authorization: Bearer <pib_agent_key>` and either `X-Org-Id: <orgId>` or rely on the key's saved `orgId`; scoped keys are rejected with 403 if the request targets another org.

Public (no-auth) endpoints — used by hosted forms / web hooks:
- `POST /email/webhook` — Resend delivery webhook receiver
- `POST /email/webhook/ses` — SES delivery webhook receiver
- `POST /capture-sources/[id]/submit` — newsletter / lead capture form submit (CORS open)
- `POST /api/embed/newsletter/[sourceId]/submit` — alias of above
- `GET  /api/embed/newsletter/[sourceId]/widget.js` — embeddable widget JS bundle
- `GET  /embed/newsletter/[sourceId]` — iframe-able signup page
- `GET  /lead/confirm/[token]` — double-opt-in confirmation page
- `POST /api/newsletter` — public newsletter signup helper
- `POST /api/preferences/[token]` — public preferences update
- `GET/POST /api/unsubscribe` — public unsubscribe link/action
- `GET /l/[code]` — public tracked short-link redirect

Additional current email utility routes:
- `DELETE /email-images/[id]` — remove an uploaded email image
- `GET/PUT/DELETE /email-snippets/[id]` — read/update/delete reusable snippets
- `GET /email-analytics/revenue/[source]/[sourceId]` — revenue attribution drilldown

## Omnichannel Communications Console

The newer Communications surface is the operational inbox and campaign layer for WhatsApp, SMS, email, in-app, Messenger, and Instagram. Use it for human/agent customer conversations, queue assignment, approved reply drafting, WhatsApp-style templates, and cross-channel communication analytics. Use the older `/broadcasts`, `/sequences`, `/email`, and `/sms` routes below for dedicated email/SMS marketing automation.

UI routes:
- `/portal/communications`
- `/portal/communications`

Channels: `whatsapp`, `sms`, `email`, `in_app`, `messenger`, `instagram`.

Providers: `twilio`, `resend`, `ses`, `in_app`, `meta`, `manual`.

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/communications/channels?orgId=...` | Returns channel accounts, queues, routing rules, provider readiness, and missing setup checks. |
| `GET` | `/communications/providers` | Lists supported communication providers and readiness. |
| `GET` | `/communications/analytics?orgId=...` | Rollup across conversations, campaigns, and events for the org. |
| `GET/POST` | `/communications/templates` | List or create message templates. `POST` requires `channel` and `content.body`; validates variables/buttons/media before saving. |
| `GET/POST` | `/communications/campaigns` | List or create channel campaigns. `POST` requires `name`, `channel`, and `templateId`; accepts audience, variable map, reply routing, and schedule. |
| `GET/POST` | `/communications/automations` | List or create automation rules with conditions/actions across channels. |
| `GET/POST` | `/communications/conversations` | List or create conversations. Filters: `status`, `channel`, `assignee`, `campaignId`, `queueId`, `priority`, `label`, `limit`. |
| `GET/PATCH` | `/communications/conversations/[id]` | Get a conversation bundle or update status, priority, queue, assignees, labels, or snooze state. |
| `GET/POST` | `/communications/conversations/[id]/messages` | List or add messages. Outbound `sendNow: true` requires `humanApproved: true` in V1. |

Conversation statuses: `new`, `open`, `pending`, `resolved`, `snoozed`.

Priorities: `low`, `normal`, `high`, `urgent`.

Message statuses: `draft`, `queued`, `sent`, `delivered`, `read`, `failed`, `received`.

Guardrails:
- Do not send customer-facing replies with `sendNow: true` unless a human explicitly approved the exact message.
- Use `status: draft` for agent-prepared replies awaiting review.
- Keep `replyRouting` or conversation assignees set when a campaign needs human follow-up.
- Check `/communications/channels` before promising WhatsApp, SMS, or social-DM delivery; readiness can be `needs_setup`, `degraded`, or missing provider credentials.

## Crons that drive this skill

- `/api/cron/emails` — every 15 min — sends `scheduled` one-off emails whose `scheduledFor <= now`
- `/api/cron/sequences` — every 15 min — advances active sequence enrollments to the next step
- `/api/cron/broadcasts` — every 15 min — sends `scheduled` broadcasts, resumes mid-flight, finalizes A/B winners, dispatches winner-only fan-out

All cron routes auth via `Authorization: Bearer ${CRON_SECRET}`.

---

# 1. Sending

## `POST /email/send` — auth: admin/ai

Send immediately via Resend. Body:
```json
{
  "orgId": "org_xyz",
  "to": "jane@acme.com",
  "cc": ["other@acme.com"],
  "subject": "Welcome to Partners in Biz",
  "bodyText": "Hi Jane,\n\n...\n\nCheers,\nPeet",
  "bodyHtml": "<p>Hi Jane...</p>",
  "contactId": "contact_abc",
  "sequenceId": "seq_xyz",
  "sequenceStep": 2
}
```

Required: `to`, `subject`, `bodyText` OR `bodyHtml`. Missing body is auto-generated from the other.

For contact-linked sends, include `contactId`; the API can derive `orgId` from that contact when the caller omitted org scope. Visual email-builder send tests may also send rendered aliases `{ "html": "...", "text": "..." }`, which are accepted as `bodyHtml` / `bodyText`.

## `POST /email/schedule` — auth: admin/ai

```json
{ ... same as /send, plus: "scheduledFor": "2026-04-20T09:00:00Z" }
```

## `GET /email` — auth: admin

Filters: `status` (`draft|scheduled|sent|failed|opened|clicked`), `direction` (`inbound|outbound`), `contactId`, `sequenceId`, `campaignId`, `broadcastId`, `page`, `limit`.

Admin/agent callers should pass `orgId` for broad email lists. For contact history reads, `GET /email?contactId=<id>&limit=...` can derive org scope from the contact and keeps Firestore index-safe by filtering secondary facets in memory.

## `GET /email/[id]` — auth: admin
## `PUT /email/[id]` — auth: admin — only if `status === 'scheduled'`
## `DELETE /email/[id]` — auth: admin — soft-delete (cancel)

## `POST /email/webhook` — **public**

Resend events handled: `email.delivered`, `email.opened`, `email.clicked`, `email.bounced`, `email.complained`. The webhook:
- updates the matching `emails` doc by `resendId`
- rolls up to `campaigns.stats` / `broadcasts.stats` / variant stats (`broadcasts.ab.variants[i].<field>` / `sequences.steps[n].ab.variants[i].<field>`)
- on `complained` → marks contact `unsubscribed`, pauses all active sequence enrollments for that contact

---

# 2. Visual Email Templates

Block-based email builder. Each template stores an `EmailDocument` = `{ subject, preheader, blocks[], theme }`. Renderer is table-based with inline styles + MSO conditionals → renders consistently in Outlook, Gmail, Apple Mail.

Block types: `hero`, `heading`, `paragraph`, `button`, `image`, `divider`, `spacer`, `columns`, `footer`.

5 starter templates ship out-of-the-box: **Weekly newsletter**, **Welcome — day one**, **Product launch**, **Re-engagement**, **Order receipt** — usable as-is or as duplication seeds.

## `GET /email-templates?orgId=...&category=...` — auth: client

Returns merged list of org-specific templates + all starters (starters have `isStarter: true`).

Categories: `newsletter | welcome | product-launch | reengagement | transactional | custom`.

## `POST /email-templates` — auth: client

Body: `{ name, description?, category, document, orgId? }`. Validates the document via the block schema. Returns `{ id }`.

## `GET /email-templates/[id]` — auth: client
## `PUT /email-templates/[id]` — auth: client — starters 403
## `DELETE /email-templates/[id]` — auth: client — starters 403

## `POST /email-templates/[id]/render` — auth: client

```json
{ "vars": { "firstName": "Jane", "company": "Acme", "unsubscribeUrl": "..." } }
```

Returns `{ html, text, subject }` with the template fully interpolated. Use this before sending to preview the final output.

## `POST /email-templates/[id]/duplicate` — auth: client

Copies a template (including starters) into the org library. Returns `{ id }`.

## `POST /email-builder/preview` — auth: client

Stateless render — body `{ document, vars? }` → `{ html, text }`. Used by the visual builder for live preview.

## `POST /email-templates/generate` — auth: client

AI-generates a new template + saves it. Body:
```json
{
  "kind": "newsletter",
  "input": { "topic": "Property launch", "voice": {...}, "stories": [...], "orgName": "Partners in Biz" },
  "orgId": "..."
}
```
Returns `{ id, name, document }`. See AI section below for full input shapes.

---

# 3. Sequences (drip campaigns)

A sequence is an ordered set of steps; each step has `delayDays`, `subject`, `bodyHtml`, `bodyText`, and optionally `ab` (A/B config — see A/B section).

Preferred CRM-scoped endpoints for portal and agent work:

- `GET /crm/sequences` — auth: cookie member+ or Bearer + `X-Org-Id`
- `POST /crm/sequences` — auth: cookie admin+ or Bearer + `X-Org-Id`
- `GET/PUT/DELETE /crm/sequences/[id]`
- `GET/POST /crm/sequences/[id]/enrollments`
- `DELETE /crm/sequences/[id]/enrollments/[enrollmentId]`

Activation rule: agents may save incomplete sequences as `draft`, but `active` sequences must have at least one step and every step must be sendable. Email steps require `subject` plus `bodyHtml` or `bodyText`; SMS steps require `smsBody`. The CRM and legacy sequence APIs reject activation with a 400 when this launch-readiness check fails.

Enrollment rule: contacts may only be enrolled into `active` sequences. Manual CRM enrollment, legacy enrollment, and CRM automation actions reject draft/paused/missing sequences before creating a `sequence_enrollments` row. For automation capture flows, use `POST /crm/automations` or `PUT /crm/automations/[id]` with an action such as `{ "type": "enroll_in_sequence", "sequenceId": "seq_active" }`; the sequence picker and API only allow active launch-ready sequences, and the executor uses the first step's `delayDays` when scheduling `nextSendAt`.

Legacy endpoints still exist for admin/property integrations:

## `GET /sequences?orgId=...&status=...` — auth: client
## `POST /sequences` — auth: client

```json
{
  "name": "SaaS Onboarding",
  "description": "5-step welcome + activation",
  "status": "draft",
  "steps": [
    { "stepNumber": 1, "delayDays": 0, "subject": "Welcome {{firstName}}",
      "bodyText": "Thanks for signing up...", "bodyHtml": "..." },
    { "stepNumber": 2, "delayDays": 2, "subject": "Day 2: Get your first value",
      "bodyText": "...", "bodyHtml": "..." }
  ]
}
```

Merge fields: `{{firstName}}`, `{{lastName}}`, `{{fullName}}`, `{{email}}`, `{{company}}`, `{{orgName}}`, `{{unsubscribeUrl}}`, plus any custom fields you supply.

## `GET/PUT/DELETE /sequences/[id]` — auth: client

## `POST /sequences/[id]/enroll` — auth: client

```json
{ "contactId": "..." }            // single
{ "contactIds": ["...", "..."] }  // batch
```

## `GET /sequence-enrollments?sequenceId=...&contactId=...&status=...` — auth: client
## `GET /sequence-enrollments/[id]` — auth: client
## `PATCH /sequence-enrollments/[id]` — auth: client — `{ "status": "paused" | "active" | "completed" }`
## `DELETE /sequence-enrollments/[id]` — auth: client

## `POST /sequences/[id]/generate` — auth: client — AI-generates steps

```json
{
  "name": "Customer onboarding",
  "goal": "Get a SaaS trial user to activate within 14 days",
  "voice": { ... see AI section ... },
  "steps": 5,
  "cadence": "normal",
  "audienceDescription": "...",
  "context": "..."
}
```
Returns `{ updated: true, steps: [...] }` and writes onto the sequence.

## `GET/PUT /sequences/[id]/steps/[stepNumber]/ab` — auth: client

A/B configuration for a single sequence step. See A/B section.

## Sequence capture routing

For CRM capture sources shown at `/portal/capture-sources`, use the CRM capture-source API and `autoSequenceIds` for direct nurture enrollment:

- `GET /crm/capture-sources`
- `POST /crm/capture-sources` with `{ name, type, autoTags?, autoCampaignIds?, autoSequenceIds?, redirectUrl?, consentRequired? }`
- `PUT /crm/capture-sources/[id]` with `{ autoSequenceIds: ["seq_..."] }`
- Public submit path: `POST /api/public/capture/[publicKey]`

On public capture, the platform dedupes contacts by `orgId + email`, applies source tags, and creates idempotent `sequence_enrollments` for each active same-org sequence in `autoSequenceIds` using `campaignId: ""`. Use `autoCampaignIds` when a campaign wrapper is needed for campaign-level stats or audience operations.

---

# 4. Broadcasts (one-time blasts / newsletters)

A broadcast is a single email blast to an audience snapshot. Use this for newsletters, announcements, one-off promotions. For ongoing nurture / multi-step, use a sequence.

## `GET /broadcasts?orgId=...&status=...&limit=...` — auth: client

Statuses: `draft | scheduled | sending | sent | paused | failed | canceled`.

## `POST /broadcasts` — auth: client

```json
{
  "orgId": "org_xyz",
  "name": "Q2 newsletter",
  "description": "Quarterly update",
  "fromDomainId": "domain_abc",
  "fromName": "Peet",
  "fromLocal": "hello",
  "replyTo": "peet@partnersinbiz.online",
  "content": {
    "templateId": "tpl_xyz",
    "subject": "What we shipped this quarter — {{firstName}}",
    "preheader": "5 new features, 3 wins",
    "bodyHtml": "",
    "bodyText": ""
  },
  "audience": {
    "segmentId": "seg_smb",
    "contactIds": [],
    "tags": [],
    "excludeUnsubscribed": true,
    "excludeBouncedAt": true
  }
}
```

Either `templateId` (uses email_templates) OR inline `bodyHtml/bodyText`. Audience: any of segmentId, contactIds, tags — they are merged and de-duped.

## `GET/PUT/DELETE /broadcasts/[id]` — auth: client

PUT only allowed when status in `[draft, paused, scheduled]`.

## `GET /broadcasts/[id]/preview` — auth: client

Returns `{ audienceSize, sampleContacts: [{ email, name, company }, ...] }` — first 5 contacts so you can sanity-check before scheduling.

## `POST /broadcasts/[id]/schedule` — auth: client

```json
{ "scheduledFor": "2026-05-20T09:00:00Z" }
```
Validates content + audience + sender. 422 with array of issues if invalid.

## `POST /broadcasts/[id]/send-now` — auth: client

Sets `scheduledFor: now` — next cron tick picks it up. Or pass `{ "immediate": true }` for synchronous send (max 100 recipients).

## `POST /broadcasts/[id]/test` — auth: client

```json
{ "to": "you@example.com", "vars": { "firstName": "Test" } }
```
Sends a one-off test render. Does NOT enroll anyone or touch stats.

## `POST /broadcasts/[id]/pause` — auth: client
## `POST /broadcasts/[id]/resume` — auth: client

## `GET /broadcasts/[id]/stats` — auth: client

```json
{
  "stats": { "audienceSize": 1245, "sent": 1240, "delivered": 1212, "opened": 488, "clicked": 102, "bounced": 28, "unsubscribed": 3, "failed": 5, "queued": 1240 },
  "rates": { "deliveryRate": 0.977, "openRate": 0.403, "clickRate": 0.084, "bounceRate": 0.023, "unsubRate": 0.0025 }
}
```

## `POST /broadcasts/[id]/generate` — auth: client — AI-generates inline content

```json
{
  "goal": "Announce the property launch to all leads",
  "voice": { ... },
  "contentLength": "medium",
  "cta": { "text": "See the launch", "url": "https://..." }
}
```
Writes subject + preheader + bodyHtml + bodyText onto the broadcast. Refuses 422 if `templateId` is already set.

## `GET/PUT /broadcasts/[id]/ab` — auth: client — A/B config (see below)
## `POST /broadcasts/[id]/ab/start` — auth: client — start winner-only test window
## `POST /broadcasts/[id]/ab/declare-winner` — auth: client — pick winner manually

---

# 5. Campaigns (sequence + audience)

A campaign ties a **sequence** to an **audience** (segment or explicit contact list) and manages enrollment in bulk. Use for multi-touch programs targeting a captured group.

## `GET /campaigns?orgId=...&status=...` — auth: client
## `POST /campaigns` — auth: client

```json
{
  "orgId": "org_xyz",
  "name": "Q2 SMB Nurture",
  "description": "Enroll all SMB leads in the 5-step nurture sequence",
  "fromDomainId": "domain_abc",
  "fromName": "Peet at Partners in Biz",
  "fromLocal": "hello",
  "replyTo": "peet@partnersinbiz.online",
  "segmentId": "seg_smb",
  "contactIds": [],
  "sequenceId": "seq_nurture_5step",
  "triggers": { "captureSourceIds": ["src_newsletter"], "tags": ["smb"] }
}
```

`triggers.captureSourceIds` auto-enrolls anyone captured via those lead-capture forms while the campaign is `active`.

## `GET/PUT/DELETE /campaigns/[id]` — auth: client
## `POST /campaigns/[id]/launch` — auth: client

Resolves audience, bulk-enrolls into the sequence. Skips: unsubscribed, bounced, cross-org, already-enrolled-for-this-campaign.

Response: `{ enrolled: 312, audienceSize: 340 }`.

## `POST /campaigns/[id]/approve-all` — auth: client (content-engine campaigns)
## `POST /campaigns/[id]/schedule` — auth: client (content-engine campaigns — bulk social posts)
## `POST /campaigns/[id]/archive` — auth: client
## `GET  /campaigns/[id]/assets` — auth: client (content-engine campaigns)

---

# 6. Segments & Audiences

## `GET /crm/segments?orgId=...` — auth: client
## `POST /crm/segments` — auth: client

```json
{
  "name": "Active SA SMBs",
  "description": "Captured via newsletter, tagged 'smb', stage 'new' or 'contacted'",
  "filters": {
    "tags": ["smb"],
    "capturedFromIds": ["src_newsletter"],
    "stage": "new",
    "type": "lead",
    "source": "form",
    "createdAfter": "2026-01-01T00:00:00Z"
  }
}
```

Filters use AND across keys, OR within `tags`/`capturedFromIds`.

## `GET /crm/segments/[id]` — auth: client
## `PUT /crm/segments/[id]` — auth: client
## `DELETE /crm/segments/[id]` — auth: client
## `GET /crm/segments/[id]/resolve?limit=...` — auth: client

Returns the live contact list matching the segment. Used by campaign/broadcast preview.

---

# 7. Lead Capture (forms, widgets, double-opt-in)

A capture source is a configurable form: define fields, styling, success behaviour, and which sequences/campaigns to auto-enroll on submit. Comes with an embeddable JS widget + iframe.

## `GET /capture-sources?orgId=...&active=...` — auth: client
## `POST /capture-sources` — auth: client

```json
{
  "orgId": "org_xyz",
  "name": "Newsletter — homepage",
  "type": "newsletter",
  "doubleOptIn": "on",
  "confirmationSubject": "Confirm your subscription",
  "confirmationBodyHtml": "<p>Click to confirm: <a href=\"{{confirmUrl}}\">Confirm</a></p>",
  "successMessage": "Check your inbox!",
  "successRedirectUrl": "https://partnersinbiz.online/thanks",
  "fields": [
    { "key": "firstName", "label": "First name", "type": "text", "required": false }
  ],
  "tagsToApply": ["newsletter", "homepage"],
  "campaignIdsToEnroll": [],
  "sequenceIdsToEnroll": ["seq_welcome"],
  "notifyEmails": ["peet@partnersinbiz.online"],
  "widgetTheme": {
    "primaryColor": "#F5A623", "textColor": "#0A0A0B", "backgroundColor": "#ffffff",
    "borderRadius": 12, "buttonText": "Subscribe",
    "headingText": "Get the weekly", "subheadingText": "One email, every Friday. Unsubscribe anytime."
  },
  "active": true
}
```

## `GET/PUT/DELETE /capture-sources/[id]` — auth: client

## `POST /capture-sources/[id]/submit` — **PUBLIC, CORS open**

```json
{ "email": "jane@example.com", "data": { "firstName": "Jane" }, "referer": "https://acme.com/" }
```

Flow:
1. Validates email
2. Creates / updates contact (orgId+email dedup, merges tags)
3. Stores submission
4. If DOI on → sends confirmation email with `{{confirmUrl}}` substituted; returns `{ ok, requiresConfirmation: true, message }`
5. If DOI off → auto-enrolls into sequenceIdsToEnroll + campaignIdsToEnroll + any active campaign whose triggers.captureSourceIds includes this source; sends `notifyEmails`; returns `{ ok, requiresConfirmation: false, message, redirect? }`

Also exposed at `POST /api/embed/newsletter/[sourceId]/submit` for cleaner embed URLs.

## `GET /capture-sources/[id]/submissions?page=...` — auth: client

## Embed surfaces

- **JS widget:** `<script src="https://partnersinbiz.online/embed/newsletter/<SOURCE_ID>/widget.js" async></script>` — renders inline (or pass `data-target="#anchor"` to mount elsewhere)
- **Iframe:** `<iframe src="https://partnersinbiz.online/embed/newsletter/<SOURCE_ID>" width="100%" height="520" style="border:0;max-width:480px"></iframe>`
- **DOI confirmation page:** `https://partnersinbiz.online/lead/confirm/<TOKEN>` — verifies HMAC, marks confirmed, runs auto-enroll

---

# 8. Email Domains (Resend verification)

## `GET /email/domains?orgId=...` — auth: client
## `POST /email/domains` — auth: client — `{ orgId, name }` → returns DNS records to add at registrar
## `GET /email/domains/[id]` — auth: client — refreshes live from Resend (poll until `status === 'verified'`)
## `DELETE /email/domains/[id]` — auth: client — soft-delete + best-effort Resend remove

Use a verified domain's `id` as `fromDomainId` on campaigns / broadcasts so sends go from `<fromLocal>@<domainName>`.

---

# 9. AI Email Generation

All generators use the same multi-kind `/email/generate` endpoint with a discriminated body.

## `POST /email/generate` — auth: client (admin/ai)

Common shape:
```json
{
  "kind": "email" | "subjects" | "sequence" | "newsletter" | "winback" | "rewrite",
  "input": { ... },
  "orgId": "org_xyz"   // optional — if set + voice not provided, voice is loaded from organizations.settings.brandVoice
}
```

### `kind: "email"` — single email

```json
{
  "kind": "email",
  "input": {
    "goal": "Follow up with cold lead after Properties demo",
    "voice": { "tone": "founder-led", "audience": "SA SMB founders", "doNotUseWords": ["leverage","supercharge"], "sampleLines": ["Most agencies juggle five tools..."], "signOff": "— Peet" },
    "audienceDescription": "SMB founder who saw the demo last week",
    "context": "They were comparing us to Mailchimp + Webflow + GA",
    "contentLength": "medium",
    "cta": { "text": "Book a 15-min call", "url": "https://cal.com/peet" },
    "outputMode": "inline"
  }
}
```

Returns:
```json
{ "subject": "...", "preheader": "...", "bodyHtml": "...", "bodyText": "...", "modelUsed": "anthropic/claude-sonnet-4.6", "generatedAt": "2026-05-11T..." }
```

For `outputMode: "document"`, returns `{ subject, preheader, document: EmailDocument, modelUsed, generatedAt }` — drop straight into `/email-templates`.

### `kind: "subjects"` — subject-line variants (A/B candidates)

```json
{ "kind": "subjects", "input": { "topic": "Properties launch", "voice": {...}, "count": 5, "body": "optional existing body" } }
```
Returns `{ subjects: ["...", "...", ...], modelUsed }`. Uses Haiku 4.5 for speed.

### `kind: "sequence"` — full nurture series

```json
{
  "kind": "sequence",
  "input": {
    "name": "Cold lead nurture",
    "goal": "...",
    "voice": {...},
    "steps": 5,
    "cadence": "normal",
    "audienceDescription": "...",
    "context": "..."
  }
}
```
Returns `{ name, description, steps: [{stepNumber, delayDays, subject, bodyHtml, bodyText}, ...], modelUsed }`.

### `kind: "newsletter"` — block-based newsletter

```json
{
  "kind": "newsletter",
  "input": {
    "topic": "What we shipped this quarter",
    "voice": {...},
    "stories": [
      { "heading": "...", "bodyHint": "...", "ctaText": "Read more", "ctaUrl": "...", "imageUrl": "..." }
    ],
    "orgName": "Partners in Biz",
    "unsubscribeUrl": "..."
  }
}
```
Returns `{ document, subject, preheader, modelUsed }` — an `EmailDocument` ready to save as a template.

### `kind: "winback"` — re-engagement

```json
{
  "kind": "winback",
  "input": {
    "contactName": "Jane",
    "contactCompany": "Acme",
    "daysSinceLastInteraction": 90,
    "lastTopicOrProduct": "Properties module",
    "voice": {...},
    "offer": { "description": "30% off COMEBACK30 for the next 14 days", "ctaText": "Reactivate now", "ctaUrl": "..." }
  }
}
```

### `kind: "rewrite"` — improve an existing body

```json
{
  "kind": "rewrite",
  "input": {
    "body": "...existing html or text...",
    "voice": {...},
    "instruction": "tighten" | "expand" | "soften" | "sharpen" | "translate-sa-english"
  }
}
```

### Voice presets (`lib/ai/voice-presets.ts`)

- `PIB_FOUNDER_VOICE` — direct, founder-led, SA English (default)
- `WARM_PROFESSIONAL` — friendly, polished service-business voice
- `BOLD_STARTUP` — startup pitch energy
- `CLINICAL_AUTHORITY` — law/health/finance
- `PLAYFUL_BRAND` — consumer / e-commerce

Pass any of these as `input.voice`. Or call `voiceFromOrg(orgId)` server-side / let the endpoint do it by passing top-level `orgId`.

### Targeted generators

- `POST /sequences/[id]/generate` — generates steps and PATCHes them onto the sequence
- `POST /broadcasts/[id]/generate` — generates inline content and writes to the broadcast
- `POST /email-templates/generate` — saves the result as a new `email_templates` doc

---

# 10. A/B Testing

A/B is configured on **broadcasts** (whole-email) and **sequence steps** (per-step). Variants override one or more of: subject, body, fromName, sendTime.

Two modes:
- **`split`** — all variants sent, weights sum to 100, optionally auto-promote winner after `testDurationMinutes`
- **`winner-only`** — variants sent only to a `testCohortPercent` of audience; after `testDurationMinutes` the system picks a winner and fans out to the remaining audience

## `GET/PUT /broadcasts/[id]/ab` — auth: client

```json
{
  "enabled": true,
  "mode": "winner-only",
  "variants": [
    { "id": "a", "label": "Short subject", "overrides": [{ "kind": "subject", "subject": "What we shipped this quarter" }], "weight": 50, "sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "bounced": 0, "unsubscribed": 0 },
    { "id": "b", "label": "Question subject", "overrides": [{ "kind": "subject", "subject": "What did we ship this quarter, Jane?" }], "weight": 50, "sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "bounced": 0, "unsubscribed": 0 }
  ],
  "testCohortPercent": 20,
  "winnerMetric": "opens",
  "testDurationMinutes": 240,
  "autoPromote": true,
  "status": "inactive",
  "winnerVariantId": "",
  "testStartedAt": null, "testEndsAt": null, "winnerDecidedAt": null
}
```

PUT validates: enabled needs ≥2 variants; split mode requires weights sum to 100; winner-only requires testCohortPercent 1-50, testDurationMinutes ≥ 5. Only editable while broadcast in `draft` or `paused`.

## `POST /broadcasts/[id]/ab/start` — auth: client

Marks `ab.status = 'testing'` and stamps `testStartedAt` + `testEndsAt`. Use for winner-only mode after scheduling.

## `POST /broadcasts/[id]/ab/declare-winner` — auth: client

```json
{ "variantId": "a" }   // manual
{}                      // auto-pick from current stats
```

Sets `ab.winnerVariantId`, transitions `ab.status = 'winner-pending'`. Next cron tick dispatches winner to the remaining audience.

## `GET/PUT /sequences/[id]/steps/[stepNumber]/ab` — auth: client

Same shape, scoped to a single sequence step.

Variant assignment is deterministic (HMAC of `contactId + ':' + broadcastId`) — re-running the same broadcast picks the same variant per contact.

---

# 11. Analytics

## `GET /email-analytics/overview?orgId=...&from=...&to=...` — auth: client

```json
{
  "range": { "from": "...", "to": "..." },
  "totals": { "sent": 1245, "delivered": 1212, "opened": 488, "clicked": 102, "bounced": 28, "unsubscribed": 3, "failed": 5 },
  "rates":  { "deliveryRate": 0.97, "openRate": 0.40, "clickRate": 0.08, "ctrOnOpens": 0.21, "bounceRate": 0.02, "unsubRate": 0.002 },
  "bySource": {
    "broadcast": { "sent": 800, "opened": 320, "clicked": 70 },
    "campaign":  { "sent": 320, "opened": 140, "clicked": 28 },
    "sequence":  { "sent": 95,  "opened": 24,  "clicked": 4 },
    "oneOff":    { "sent": 30,  "opened": 4,   "clicked": 0 }
  },
  "topBroadcasts": [{ "id": "...", "name": "...", "sent": 800, "opened": 320, "clicked": 70, "openRate": 0.4, "clickRate": 0.087 }],
  "topCampaigns": [...],
  "worstBounces": [...]
}
```

## `GET /email-analytics/timeseries?orgId=...&from=...&to=...&bucket=day|week` — auth: client

```json
{ "range": {...}, "bucket": "day", "series": [{ "date": "2026-04-01", "sent": 12, "delivered": 12, "opened": 5, "clicked": 1, "bounced": 0 }, ...] }
```

## `GET /email-analytics/broadcasts/[id]` — auth: client
Per-broadcast detail (KPIs + timeline + topClicks + topDomains).

## `GET /email-analytics/sequences/[id]` — auth: client
Per-sequence identity, status breakdown, step funnel, and agent-ready optimization guidance.

Returns:
- `sequence`: `{ id, name, description, status, stepsCount }`
- `totalEnrollments`, `byStatus`, `averageCompletionDays`
- `stepFunnel`: per-step sent/open/click/drop-off metrics
- `insights`: completion/open/click rates, `weakestStepNumber`, and `nextActions` for agents/operators

Portal users can reach sequence reporting from `/portal/email-analytics`: active `/crm/sequences` appear in the `Sequence performance` list and link to `/portal/email-analytics/sequences/[id]`. Use that drilldown to inspect enrollment status, active/completed counts, average completion days, step-level sent/open/click/drop-off data, and the `Agent next moves` recommendations. Agents should use `insights.nextActions` as the starting checklist when optimizing a sequence.

## `GET /email-analytics/contacts?orgId=...&status=highly-engaged|engaged|cooling|dormant|unsubscribed|bounced&limit=...` — auth: client

Engagement-scored contacts (score 0..100). Status buckets derived from score + recency.

## `GET /email-analytics/leaderboard?from=...&to=...` — auth: **admin/ai only**

Cross-org leaderboard — open rate / click rate / bounce rate per org. Platform-admin tool.

---

# 12. Tracked short links (CTA click stats)

## `GET /links?orgId=...` — auth: client
## `POST /links` — auth: client — `{ targetUrl, slug?, description? }` → `{ id, slug, shortUrl }`
## `GET/PUT/DELETE /links/[id]` — auth: client (slug immutable)
## `GET /links/[id]/stats` — auth: client — clicks, referrers, countries, day/hour buckets

Public route `/l/<slug>` logs the click + 302s to targetUrl.

---

# Workflow guides (agent-ready recipes)

## 1. Newsletter signup widget on a client's marketing site

```bash
# Create the capture source
POST /capture-sources
{ "orgId":"acme", "name":"Newsletter — homepage", "type":"newsletter",
  "doubleOptIn":"on", "successMessage":"Check your inbox!",
  "fields":[{"key":"firstName","label":"First name","type":"text","required":false}],
  "tagsToApply":["newsletter"], "sequenceIdsToEnroll":["seq_welcome_3step"],
  "notifyEmails":["peet@partnersinbiz.online"],
  "widgetTheme":{"primaryColor":"#F5A623","textColor":"#0A0A0B","backgroundColor":"#fff","borderRadius":12,"buttonText":"Subscribe","headingText":"Get the weekly","subheadingText":"One email, every Friday."},
  "active":true }
# → { id: "src_abc" }

# Have the client paste this into their site:
<script src="https://partnersinbiz.online/embed/newsletter/src_abc/widget.js" async></script>

# Every signup → contact created/updated, DOI email sent, after confirmation → enrolled in seq_welcome_3step.
```

## 2. AI-generate a 5-step nurture sequence + activate it

```bash
# Create empty sequence
POST /sequences
{ "name":"SaaS onboarding", "description":"5-step onboarding", "status":"draft", "steps":[] }
# → { id: "seq_abc" }

# Have AI fill it in
POST /sequences/seq_abc/generate
{ "name":"SaaS onboarding", "goal":"Get a trial user to activate in 14 days",
  "voice": <PIB_FOUNDER_VOICE>, "steps":5, "cadence":"normal" }

# Activate
PUT /sequences/seq_abc { "status":"active" }

# Enroll contacts captured via the form
POST /sequences/seq_abc/enroll { "contactIds": [...] }
```

## 3. Newsletter broadcast with A/B subject test

```bash
# Newsletter from template
POST /broadcasts
{ "orgId":"acme", "name":"April newsletter",
  "fromDomainId":"dom_acme", "fromName":"Acme Studio", "fromLocal":"hello",
  "content":{"templateId":"tpl_newsletter_apr","subject":"What's new this month","preheader":"3 stories + 1 win","bodyHtml":"","bodyText":""},
  "audience":{"segmentId":"seg_active","contactIds":[],"tags":[],"excludeUnsubscribed":true,"excludeBouncedAt":true} }
# → { id: "bc_abc" }

# Generate 5 subject variants
POST /email/generate
{ "kind":"subjects", "input":{ "topic":"April newsletter recap", "voice": <PIB_FOUNDER_VOICE>, "count":5 } }
# → { subjects: ["...", "..."] }

# Wire 2 winners as A/B variants
PUT /broadcasts/bc_abc/ab
{ "enabled":true, "mode":"winner-only", "testCohortPercent":20, "winnerMetric":"opens",
  "testDurationMinutes":240, "autoPromote":true,
  "variants":[
    {"id":"a","label":"Short","overrides":[{"kind":"subject","subject":"<short>"}],"weight":50,"sent":0,"delivered":0,"opened":0,"clicked":0,"bounced":0,"unsubscribed":0},
    {"id":"b","label":"Question","overrides":[{"kind":"subject","subject":"<question>"}],"weight":50,"sent":0,"delivered":0,"opened":0,"clicked":0,"bounced":0,"unsubscribed":0}
  ]}

# Sanity-check the audience
GET /broadcasts/bc_abc/preview
# → { audienceSize: 1245, sampleContacts: [...] }

# Schedule
POST /broadcasts/bc_abc/schedule { "scheduledFor":"2026-05-15T09:00:00Z" }

# Start the A/B window once it goes 'scheduled' — the cron will dispatch the test cohort first
POST /broadcasts/bc_abc/ab/start

# 4h later the cron auto-picks the winner and fans out to the remaining 80%.
# Or manually:
POST /broadcasts/bc_abc/ab/declare-winner { "variantId":"a" }

# Watch it
GET /broadcasts/bc_abc/stats
GET /email-analytics/broadcasts/bc_abc
```

## 4. Verify a custom sending domain

```bash
POST /email/domains { "orgId":"acme", "name":"mail.acme.com" }
# → { id, dnsRecords:[...] }

# Add each record at the registrar, then poll:
GET /email/domains/dom_acme
# Repeat until status === 'verified'
```

## 5. Send a one-off email with a tracked CTA

```bash
POST /links { "targetUrl":"https://acme.com/landing?utm_source=email&utm_campaign=apr", "slug":"apr" }
# → { shortUrl: "https://partnersinbiz.online/l/apr" }

POST /email/send
{ "to":"jane@acme.com", "subject":"Quick follow-up",
  "bodyHtml":"<p>Hi Jane, ...<a href=\"https://partnersinbiz.online/l/apr\">See the offer</a></p>",
  "contactId":"contact_abc" }

# Later
GET /links/<id>/stats
```

## 6. Re-engagement campaign for cooling contacts

```bash
# Find cooling contacts via analytics
GET /email-analytics/contacts?orgId=acme&status=cooling&limit=200
# → array with contactIds

# Generate a winback email
POST /email/generate
{ "kind":"winback",
  "input":{ "contactName":"{{firstName}}", "daysSinceLastInteraction":60,
    "voice":<PIB_FOUNDER_VOICE>,
    "offer":{"description":"30% off COMEBACK30 for the next 14 days","ctaText":"Reactivate","ctaUrl":"https://..."} } }

# Save as a one-shot broadcast and send-now
POST /broadcasts
{ "orgId":"acme", "name":"Winback April",
  "content":{ "subject":"<from above>", "bodyHtml":"<from above>", "bodyText":"<from above>", "templateId":"", "preheader":"" },
  "audience":{ "segmentId":"", "contactIds":<from analytics>, "tags":[], "excludeUnsubscribed":true, "excludeBouncedAt":true }, ... }
POST /broadcasts/<id>/send-now
```

---

# Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `to is required` / `subject is required` | Supply fields |
| 400 | `bodyText or bodyHtml is required` | At least one body |
| 400 | `scheduledFor must be in the future` | Check timestamp |
| 400 | `name is required` | Required for sequence/campaign/broadcast/template |
| 400 | `Invalid document` | Validate block shape — see `/email-builder/preview` for live errors |
| 400 | `Invalid domain name` | Use a valid domain format (e.g. `mail.acme.com`) |
| 400 | `At least 2 variants are required when A/B testing is enabled` | Add a second variant |
| 400 | `Variant weights must sum to 100 in split mode` | Adjust weights |
| 400 | `testCohortPercent must be between 1 and 50` | winner-only constraint |
| 403 | `Starters are read-only` | Duplicate instead of editing |
| 404 | not found | Verify id, not soft-deleted |
| 409 | `Cannot edit a sent email` | Only scheduled/draft are editable |
| 409 | `Domain already registered for this org` | Use the existing record |
| 409 | `A/B config can only be edited while broadcast is draft or paused` | Pause first |
| 422 | `Campaign has no sequence` / `has no audience` | Set the missing field |
| 422 | `Audience is empty` | Segment resolved to zero contacts |
| 422 | `Sequence has no steps` | Add at least one step |
| 422 | `Cannot generate inline content — template is set` | Clear `content.templateId` first |
| 502 | `Resend rejected the domain` | Domain name invalid or Resend API error |

---

# Agent patterns

1. **Always link `contactId`** on `/email/send` so the contact's activity timeline is clean.
2. **Voice presets are your shortcut** — pass `PIB_FOUNDER_VOICE` for PiB-style; or supply `orgId` and the endpoint loads `org.settings.brandVoice` if defined.
3. **Use templates over inline HTML.** Build once via the visual builder, reference by `templateId` on every broadcast — far easier to maintain.
4. **Preview before sending.** `POST /email-templates/[id]/render` + `GET /broadcasts/[id]/preview` together tell you exactly who gets exactly what.
5. **Generate subject variants for every broadcast** — `POST /email/generate {kind:"subjects"}` then wire the top 2 into `/ab` config. Use `mode:"winner-only"` with `autoPromote:true` for hands-off A/B.
6. **Newsletter signup must use DOI.** GDPR / SA POPI compliance + better deliverability + cleaner list.
7. **Watch the bounce + complaint rates.** A single complaint flags; 3+ in 7 days → pause sending and investigate. `GET /email-analytics/overview` shows `bounceRate` and `unsubRate`.
8. **Tracked links on every CTA.** `POST /links` first, then embed `shortUrl` — automatic click attribution.
9. **Segment + tag — not raw contactIds — for ongoing programs.** A segment evaluates fresh on each campaign launch; a contactIds list is frozen at the time of POST.
10. **`fromDomainId` must be `verified`.** Sends from an unverified domain fall back to the shared PiB domain — fine for early experiments, bad for client-branded sends.
11. **Idempotency**: every POST that creates a resource supports `Idempotency-Key` header. The broadcast cron is itself idempotent (`emails` collection has a unique `broadcastId+contactId` invariant — the cron skips already-sent contacts).
12. **A/B is deterministic per contact.** Re-running a paused/restarted broadcast routes each contact to the same variant. No double-counting.
13. **Engagement score (0..100)** = `opens × 5 + clicks × 15 − bounces × 30 − daysSinceLastEngaged × 0.5`, clamped. Use the `cooling`/`dormant` status filters on `/email-analytics/contacts` to find your winback audience.
14. **No raw HTML in starters.** All 5 starter templates use the block model — easier to AI-edit, easier to remix per-org.
15. **The complete capture → enroll loop:** `/capture-sources/[id]/submit` (public) → contact + tags applied → DOI confirm if on → auto-enroll all matching sequences + active campaigns whose `triggers.captureSourceIds` includes the source. No glue code needed.

---

# v3 features (2026-05-11 world-class build)

Twelve additional layers on top of the v2 platform. Every surface is agent-callable.

## 13. Deliverability hardening

- **List-Unsubscribe + List-Unsubscribe-Post (RFC 8058 one-click)** — `sendCampaignEmail` accepts `listUnsubscribeUrl`; every broadcast/sequence/transactional send now sets `List-Unsubscribe: <url>` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click`. Required by Gmail/Yahoo bulk-sender rules.
- **Bounce categorization** — webhook reads `data.bounce.{type,subType}`. Hard → permanent suppression + `contact.bouncedAt`. Soft → temporary 24h suppression (contact stays sendable after expiry). Complaint → permanent suppression + full unsubscribe.
- **Suppression list** — `suppressions` collection keyed by `${orgId}_${lowercase(email)}`. Reasons: `hard-bounce | soft-bounce | complaint | manual-unsub | list-cleanup | invalid-address | disposable-domain`. Scopes: `permanent | temporary`. Routes:
  - `GET /api/v1/suppressions?orgId=...&reason=...` — list
  - `POST /api/v1/suppressions` — admin add
  - `DELETE /api/v1/suppressions/[id]` — admin remove
  - `GET /api/v1/suppressions/check?orgId=...&email=...` — `{ suppressed, reason, scope, expiresAt }`
- **Send pipelines refuse suppressed addresses** — `lib/broadcasts/audience.ts` filters via `getSuppressedEmails`; `sendSmsToContact` and `sendBroadcastToContact` and the sequences cron all call `isSuppressed` before sending.
- **Webhook svix verification** — `app/api/v1/email/webhook` enforces `svix-id/timestamp/signature` headers against `RESEND_WEBHOOK_SECRET`. Soft-fails with warning in dev when secret unset; MANDATORY in prod.

## 14. Spam protection on lead capture

`CaptureSource` extended with:
```ts
turnstileEnabled: boolean
turnstileSiteKey: string
honeypotEnabled: boolean             // default true
blockDisposableEmails: boolean       // default true (40+ burner domains)
rateLimit: { enabled: boolean; maxPerHourPerIp: number; maxPerDayPerEmail: number }
```

- Cloudflare Turnstile widget injected into JS bundle + iframe; verified server-side via `TURNSTILE_SECRET_KEY`.
- Honeypot `_hp` field included in every form (CSS-hidden). Filled = silent success (fool the bot).
- Rate limit state in `lead_capture_rate_limits` collection, deterministic keys.
- Disposable email check via `lib/lead-capture/disposable-domains.ts > isDisposableEmail`.
- Block stats incremented on `source.stats.blocked.{honeypot,rateLimit,disposable,captcha}`.
- Admin "Spam protection" tab in CaptureSourceEditor.

## 15. Preferences center + frequency capping

Instead of binary unsubscribe, contacts pick topics + frequency.

- **`SubscriptionTopic`** per-org config in `org_preferences_config/{orgId}` — list of topics + page copy + default frequency.
- **`ContactPreferences`** in `contact_preferences/{contactId}` — `topics: Record<topicId, boolean>`, `frequency: 'all'|'weekly'|'monthly'|'transactional-only'|'none'`.
- **Preferences page** at `/preferences/[token]` — same HMAC token as unsubscribe. Server-rendered form works without JS.
- **`shouldSendToContact({ contactId, orgId, topicId? })`** — SINGLE SOURCE OF TRUTH for "can I send to this contact". Every cron/send path calls it.
- **Frequency cap** in `organizations.settings.frequencyCap`: `maxPer7Days` (default 7), `maxPer24Hours` (default 3), `exemptTopics: ['transactional']`.
- **`isWithinFrequencyCap(orgId, contactId, topicId)`** — counts emails in last 24h/7d, excludes exempt topics. Frequency-skipped sends logged to `frequency_skips`.
- **`topicId`** added to Broadcast, Sequence, and Email docs.

Routes:
- `GET/PUT /api/v1/orgs/[orgId]/preferences-config`
- `GET /api/v1/orgs/[orgId]/preferences-config/recent-unsubs`
- `GET/PUT /api/v1/orgs/[orgId]/frequency-cap`
- `GET/PUT /api/v1/contacts/[id]/preferences`

Footer block auto-injects `{{preferencesUrl}}` when not explicitly set.

## 16. broadcast_recipients drain (A/B winner-only fix)

The broadcast cron's main loop now drains `broadcast_recipients` after the main loop. For A/B winner-only mode, deferred contacts pending the winner now actually get the winner variant sent. Idempotent via existing `(broadcastId, contactId)` emails-doc check. Cron response includes `recipientsDrained`/`recipientsFailed`/`recipientsSkipped`.

## 17. Reply tracking (Resend Inbound)

- **Webhook:** `POST /api/v1/email/inbound-webhook` (public, svix-verified).
- **Collection:** `inbound_emails` — one doc per received message with intent classification.
- **Classifier:** header-aware (`Auto-Submitted`, `X-Autoreply`, `Precedence`, `X-Failed-Recipients`, DSN Content-Type) + subject prefix + body unsubscribe-phrase scan.
- **5 intents:**
  - `reply` — auto-pauses active `sequence_enrollments` with `exitReason: 'replied'`, bumps `contact.lastRepliedAt` + `repliesCount`
  - `auto-reply` — log only, no pause
  - `bounce-reply` — adds soft-bounce suppression, marks `contact.bouncedAt`
  - `unsubscribe-reply` — full unsub + permanent manual-unsub suppression + pause all enrollments
  - `unknown` — log + notify admins via `org.settings.replyNotifyEmails`
- **Admin UI:** `/portal/email` list + detail with intent badges.

**Config required:** Create a Resend Route in dashboard forwarding inbound `reply.<sending-domain>` to `https://partnersinbiz.online/api/v1/email/inbound-webhook`. Set sequence/broadcast `replyTo` to that address.

## 18. Send-time optimization (timezone-aware)

- **Org-level:** `OrgSettings.preferredSendHourLocal` (default 9), `preferredSendDaysOfWeek` (default `[1,2,3,4,5]` Mon-Fri).
- **Per-contact override:** `Contact.timezone` (IANA).
- **Sequences cron:** `nextSendAt = pickSendTime(now + delayDays, ctx)` — DST-correct via `Intl.DateTimeFormat` roundtrip (no offset-string math).
- **Broadcast local delivery:** new `broadcast.audienceLocalDelivery` + `localDeliveryWindowHours` (default 24). When on, cron defers contacts whose local clock hasn't reached the broadcast hour. After windowHours expires, sends regardless. Admin: "Deliver at recipient's local time" checkbox in BroadcastEditor Schedule tab.

## 19. Behavioral segmentation

`SegmentFilters` extended (all OPTIONAL — old segments keep working):

```ts
behavioral?: BehavioralRule[]      // AND across rules
engagement?: EngagementScoreRule
```

- **8 ops × 7 scopes:** `has-opened|has-not-opened|has-clicked|has-not-clicked|has-received|has-not-received|has-replied|has-not-replied` × `any-email|broadcast|campaign|sequence|sequence-step|topic|link-url`.
- **Engagement filter:** min/max score (0-100), `lastEngagedWithinDays`, `notEngagedWithinDays`.
- **Live preview:** `POST /api/v1/crm/segments/preview` returns `{ count, sample }` without persisting.
- **7 predefined recipes** in `lib/crm/predefined-segments.ts`: Highly engaged / Cooling / Dormant / New & active / Never engaged / Clicked but didn't reply / Newsletter-only. Use as templates in the UI.

## 20. Branching sequences + goal-based exit + wait-until

`SequenceStep` extended with OPTIONAL `branch?: SequenceBranch` and `waitUntil?: WaitUntil`. `Sequence` extended with optional `goals?: SequenceGoal[]`.

- **Branch conditions:** `opened | not-opened | clicked | not-clicked | clicked-link | contact-has-tag | contact-at-stage | replied | days-since-step | goal-hit`.
- **Wait-until:** `business-hours | day-of-week | contact-tag-added | contact-stage-reached | goal-hit`. With `maxWaitDays` + `onTimeout: 'send' | 'exit'`.
- **Goals:** checked before every step. Hit → exit with custom `exitReason` (e.g. `'converted'`).
- **Cycle guard:** `visitedSteps[]` on enrollment; revisit triggers `exitReason: 'cycle-detected'`.
- **Path audit trail:** `path: EnrollmentPathEntry[]` on enrollment records every step + branch decision.
- **`pendingBranchEvalAt`** on enrollment — two-phase send → wait → branch flow.

Routes:
- `PATCH /api/v1/sequences/[id]/steps/[stepNumber]` — set branch/waitUntil
- `PUT /api/v1/sequences/[id]/goals` — set sequence goals
- `GET /api/v1/sequence-enrollments/[id]/path` — view contact's journey

Admin UI: ConditionPicker, BranchEditor, WaitUntilEditor, GoalsEditor components + `SequenceTreeView` visualization.

## 21. Pre-send preflight validation

Catches mistakes BEFORE sending.

Checks: subject length, missing alt text, broken/empty link URLs, low-contrast text, missing unsubscribe link, oversize images, banned-word audit.

Routes:
- `POST /api/v1/broadcasts/[id]/preflight` — returns `{ errors[], warnings[], passed }`
- `POST /api/v1/sequences/[id]/steps/[stepNumber]/preflight` — same for a sequence step

Admin: `PreflightPanel` component in BroadcastEditor + sequence step editor. Schedule button disabled if errors present.

## 22. A/B statistical significance

`lib/ab-testing/stats.ts > selectWinner` now respects `minSampleSize` (default 100 per variant). Returns null until both variants have enough data. Optional chi-squared test reports confidence level. Manual override still works via `POST /broadcasts/[id]/ab/declare-winner { variantId }`.

## 23. Image upload + brand kit + conditional content + reusable snippets

- **Image upload:** `POST /api/v1/email-images/upload` — multipart upload to Firebase Storage, returns CDN URL. Used by builder image block.
- **Brand kit:** `GET/PUT /api/v1/brand-kit` per-org store of logo URL, primary/secondary/accent colors, font family, custom voice, default footer. Auto-applied to new templates via `applyToDocument`.
- **Conditional content blocks:** every block now supports `condition?: BlockCondition` — show/hide based on contact tag, stage, custom field, or merge-var presence. Renderer evaluates per-recipient.
- **Reusable snippets:** save a block tree as a named snippet, reuse across templates. CRUD via `/api/v1/email-snippets`. Pre-built snippets in `snippet-presets.ts` (header / footer / hero card / CTA bar / social row). Creative Canvas can also publish a node as an `email_block` (target of `POST /api/v1/creative-canvas/[id]/exports/draft`), which auto-creates an inert `custom`-category snippet (paragraph from the node text + image block from its output URL) — it appears in the snippet library but nothing is sent or scheduled.

## 24. Popup / exit-intent / multi-step capture widgets

`CaptureSource.display: WidgetDisplayConfig` with 5 modes:

- **inline** (default) — current behavior
- **popup** — modal after `triggerDelaySeconds` or `triggerScrollPercent`; optional `triggerOnExitIntent`
- **slide-in** — small toaster from `position: bottom-right | bottom-left | top-right | top-left`
- **exit-intent** — fires on mouseleave (desktop) or popstate (mobile)
- **multi-step** — collects email first, then progressive profiling on subsequent steps

Per-mode controls: `dismissCooldownDays` (default 7), `suppressForSubscribedDays` (default 365), `showOnPaths` / `hideOnPaths` (glob patterns), `triggerPagesViewed`. Frequency state in `localStorage` under `pib_lc_<sourceId>_*`.

- `POST /api/v1/capture-sources/[id]/progressive` — partial multi-step submits (captures email on step 1 even if user bails on step 2).
- Admin "Display & triggers" tab in CaptureSourceEditor with live preview iframe.

## 25. AMP for Email + dark mode + interactive blocks

4 new AMP block types:

- `amp-carousel` — multi-image slider with autoAdvance
- `amp-accordion` — expandable FAQ sections
- `amp-form` — capture inside the email (no click-through needed)
- `amp-live-data` — fetch live JSON at render time

HTML fallbacks for non-AMP clients (first slide, fully-expanded accordions, "Click to subscribe" buttons).

- **AMP renderer:** `lib/email-builder/render-amp.ts > renderAmpEmail(doc, vars)` returns `null` if no AMP blocks (skip AMP entirely).
- **Dark mode:** `<meta name="color-scheme" content="light dark">` + `@media (prefers-color-scheme: dark)` CSS overrides + MSO Outlook 365 `[data-ogsc]` selectors. Theme override `darkMode: 'auto' | 'force-light'`.
- **AMP validation:** `validateAmp(ampHtml)` checks for AMP 4 Email boilerplate before send.

## 26. Advanced analytics

5 new endpoints + 4 new dashboard tabs:

- **Cohort retention:** `GET /api/v1/email-analytics/cohort?orgId=...&from=...&to=...&weeksToShow=12` — % of each signup-week cohort engaged in each subsequent week.
- **Revenue attribution:** `GET /api/v1/email-analytics/revenue` (overview) + `GET /revenue/[source]/[sourceId]`. Auto-attributes on deal `won` and invoice `paid`. Stored in `email_attributions` keyed by `${orgId}_${conversionId}`.
- **Click heatmap:** `GET /api/v1/email-analytics/broadcasts/[id]/heatmap` — link-by-link click stats with position in email.
- **Send-time matrix:** `GET /api/v1/email-analytics/send-time-matrix?orgId=...&from=...&to=...` — 7×24 grid of openRate per (day, hour) in org timezone. Includes `bestDay`/`bestHour` recommendation (min 10 samples per cell).
- **Industry benchmarks:** `GET /api/v1/email-analytics/benchmarks?orgId=...&industry=...&from=...&to=...` — compares org's rates to industry medians (newsletter/ecommerce/saas/agency/nonprofit/b2b/media/finance/health) and to org's own 30-day rolling baseline. Reports p25/p50/p75 percentile bucket per metric.

Dashboard tabs: Cohorts (heatmap table), Revenue (KPIs + topPerformingEmails + topPerformingSources), Send time (7×24 grid with best-time recommendation), Benchmarks (3-column comparison).

## 27. SMS via Twilio + multi-channel sequences

- **Library:** `lib/sms/twilio.ts` (SDK wrapper + `isValidE164` / `normalizeToE164` / `countSmsSegments`), `lib/sms/send.ts > sendSmsToContact` (preferences gate + suppression + activity log + stats roll-up).
- **`Sms` collection** with same shape patterns as `emails`: direction, twilioSid, status, segmentsCount, costEstimateUsd, contactId, sequenceId, broadcastId, topicId, variantId.
- **Contact extensions:** `phoneVerified?`, `smsOptedIn?`, `smsUnsubscribedAt?`.
- **Suppression extended with `channel: 'email' | 'sms'`.**
- **Multi-channel sequence steps:** `SequenceStep.channel: 'email' | 'sms'` + `smsBody`. Cron dispatches on channel.
- **Multi-channel broadcasts:** `Broadcast.channel: 'email' | 'sms'`. SMS broadcasts use `content.bodyText` as the SMS body. A/B variants also apply to SMS.
- **Routes:**
  - `POST /api/v1/sms/send` — send (ad-hoc or contact-aware)
  - `GET  /api/v1/sms` / `GET /api/v1/sms/[id]` — list/detail
  - `POST /api/v1/sms/webhook` — PUBLIC, Twilio-signature verified. Handles STOP/HELP/START keywords (TwiML responses for HELP, suppression+confirmation for STOP).
  - `POST /api/v1/sms/status-webhook` — PUBLIC, status callbacks (sent → delivered/failed/undelivered). Rolls up broadcast/campaign stats. Adds SMS suppression on hard-fail Twilio error codes (21610 = STOP, 21211/21408/21614/30003-30008 = hard).
- **AI SMS generator:** `POST /api/v1/email/generate { kind: 'sms', input: { goal, voice, cta?, maxSegments? } }` — uses BRIEF_MODEL (Haiku) since SMS is short.
- **Admin UI:** channel toggle in BroadcastEditor + sequence step editor. SMS view shows segment counter (chars · segments · GSM7/UCS2).
- **Env required:** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_MESSAGING_SERVICE_SID`, `TWILIO_DEFAULT_FROM_NUMBER`.

## v3 workflow recipe — complete world-class campaign

```bash
# 1. Create a brand kit
PUT /api/v1/brand-kit
{ "orgId":"acme", "logoUrl":"...", "primaryColor":"#0A0A0B", "accentColor":"#F5A623",
  "fontFamily":"Inter, sans-serif", "footer":{ "address":"Cape Town, SA" } }

# 2. Set up preferences + frequency cap
PUT /api/v1/orgs/acme/preferences-config
{ "topics":[{"id":"newsletter","label":"Weekly newsletter","defaultOptIn":true},
            {"id":"product-updates","label":"Product updates","defaultOptIn":true},
            {"id":"transactional","label":"Receipts & account","defaultOptIn":true}],
  "defaultFrequency":"all", "enabled":true }

PUT /api/v1/orgs/acme/frequency-cap
{ "enabled":true, "maxPer7Days":5, "maxPer24Hours":2, "exemptTopics":["transactional"] }

# 3. Create a popup lead-capture form
POST /api/v1/capture-sources
{ "orgId":"acme", "name":"Homepage exit-intent", "type":"newsletter",
  "doubleOptIn":"on", "turnstileEnabled":true, "turnstileSiteKey":"0x4AAA...",
  "blockDisposableEmails":true, "honeypotEnabled":true,
  "rateLimit":{"enabled":true,"maxPerHourPerIp":10,"maxPerDayPerEmail":3},
  "display":{ "mode":"exit-intent", "triggerOnExitIntent":true,
    "dismissCooldownDays":7, "suppressForSubscribedDays":365 },
  "sequenceIdsToEnroll":["seq_welcome"], "active":true }

# 4. Build a behavioral segment
POST /api/v1/crm/segments
{ "orgId":"acme", "name":"Engaged-but-no-purchase",
  "filters":{
    "behavioral":[
      { "op":"has-opened", "scope":"any-email", "withinDays":30 },
      { "op":"has-not-clicked", "scope":"link-url", "scopeId":"checkout" }
    ],
    "engagement":{ "min":30 } } }

# 5. AI-generate newsletter content with A/B subject variants
POST /api/v1/email/generate
{ "kind":"newsletter", "input":{ "topic":"April recap", "voice":<PIB_FOUNDER_VOICE>,
  "stories":[ {"heading":"...","bodyHint":"...","ctaText":"Read","ctaUrl":"..."} ], "orgName":"Acme" } }
POST /api/v1/email/generate { "kind":"subjects", "input":{ "topic":"April recap", "voice":<PIB_FOUNDER_VOICE>, "count":5 } }

# 6. Create broadcast with local-delivery + A/B + send-time optimization
POST /api/v1/broadcasts
{ "orgId":"acme", "name":"April newsletter", "channel":"email", "topicId":"newsletter",
  "audienceLocalDelivery":true, "localDeliveryWindowHours":24,
  "content":{ "templateId":"<from step 5>" },
  "audience":{ "segmentId":"<from step 4>","excludeUnsubscribed":true,"excludeBouncedAt":true } }

PUT /api/v1/broadcasts/<id>/ab
{ "enabled":true, "mode":"winner-only", "testCohortPercent":20, "winnerMetric":"opens",
  "testDurationMinutes":240, "autoPromote":true,
  "variants":[{"id":"a","weight":50,"overrides":[{"kind":"subject","subject":"<v1>"}],...},
              {"id":"b","weight":50,"overrides":[{"kind":"subject","subject":"<v2>"}],...}] }

# 7. Preflight validation
POST /api/v1/broadcasts/<id>/preflight
# → { passed: true, warnings: [], errors: [] }

POST /api/v1/broadcasts/<id>/schedule { "scheduledFor":"2026-05-15T09:00:00+02:00" }
POST /api/v1/broadcasts/<id>/ab/start

# 8. Follow-up SMS to non-openers after 3 days (in a sequence)
POST /api/v1/sequences
{ "name":"April recap follow-up", "topicId":"newsletter", "status":"active",
  "steps":[
    { "stepNumber":1, "delayDays":3, "channel":"sms",
      "smsBody":"Hi {{firstName}}, missed our April recap. 30sec read: {{shortUrl}}",
      "branch":{ "rules":[{"condition":{"kind":"clicked"},"nextStepNumber":-1,"evaluateAfterDays":2}],
                 "defaultNextStepNumber":1 } }
  ] }

# 9. Watch the funnel
GET /api/v1/email-analytics/overview?orgId=acme&from=2026-05-01&to=2026-05-31
GET /api/v1/email-analytics/cohort?orgId=acme&from=2026-04-01&to=2026-05-31
GET /api/v1/email-analytics/broadcasts/<id>/heatmap
GET /api/v1/email-analytics/benchmarks?orgId=acme&industry=newsletter
GET /api/v1/email-analytics/send-time-matrix?orgId=acme&from=2026-04-01&to=2026-05-31

# 10. Revenue attribution lands automatically when contacts convert
# (deal stage→won OR invoice→paid triggers `recordAttribution` server-side)
```

## v3 agent patterns

16. **Always check preflight before scheduling.** `POST /broadcasts/[id]/preflight` catches broken links, missing alt text, missing unsubscribe.
17. **Use the preferences gate.** `shouldSendToContact` is the canonical "may I send?" check — your custom code should NEVER bypass it.
18. **Suppression list is the single source of truth.** Don't query `contacts.bouncedAt` directly — `isSuppressed(orgId, email, channel?)` covers all reasons + temporary/permanent.
19. **Multi-channel = email + SMS** in one sequence. Step 1 email, step 2 SMS, step 3 email again. Set `channel: 'sms'` + `smsBody` on the step.
20. **Behavioral segments evaluate live.** `POST /crm/segments/preview` is your debug tool — never schedule a broadcast without checking the count.
21. **Local delivery beats global timestamp** for newsletters. `audienceLocalDelivery: true` + `localDeliveryWindowHours: 24` sends at 9am wherever each contact is.
22. **Branching beats linear** for nurture. After a key email, branch on opened/clicked/replied → different paths.
23. **Goals exit aggressively.** When the goal of the sequence is achieved (deal won, demo booked), stop sending. Set `sequence.goals[]`.
24. **A/B needs ≥100 samples per variant** before the auto-winner picks. Don't trust 5-vs-4 splits.
25. **Industry benchmarks calibrate your reporting.** `GET /email-analytics/benchmarks` answers "is 22% open rate good?" with the right context.
26. **Cohort retention reveals churn.** A cohort that drops from 40% engaged in week 1 to 5% by week 4 = welcome series isn't activating. Watch week-1 retention closely.
27. **Send-time matrix > "always 9am".** After 100+ sends, `GET /send-time-matrix` shows when YOUR contacts actually open. Often surprising.
28. **For Resend Inbound:** add the Route in the dashboard before relying on reply tracking. Point `replyTo` at the routed address.
29. **For Twilio Webhooks:** configure inbound + status callback URLs in Messaging Service settings. `TWILIO_AUTH_TOKEN` enforces signature verification.
30. **For Cloudflare Turnstile:** site key embeds publicly in the widget; secret key (`TURNSTILE_SECRET_KEY`) stays server-side.

# Required env vars (full list)

```
# Resend
RESEND_API_KEY=re_...
RESEND_WEBHOOK_SECRET=whsec_...

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_MESSAGING_SERVICE_SID=MG...
TWILIO_DEFAULT_FROM_NUMBER=+27...

# Cloudflare Turnstile (for lead-capture)
TURNSTILE_SECRET_KEY=0x4AAA...

# Tokens
UNSUBSCRIBE_TOKEN_SECRET=...   # HMAC secret for unsubscribe + preferences URLs
LEAD_CONFIRM_TOKEN_SECRET=...  # HMAC secret for DOI tokens (falls back to UNSUBSCRIBE_TOKEN_SECRET)

# Cron
CRON_SECRET=...

# URLs
NEXT_PUBLIC_APP_URL=https://partnersinbiz.online
NEXT_PUBLIC_BASE_URL=https://partnersinbiz.online
```
