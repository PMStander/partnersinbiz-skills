---
name: billing-finance
description: >
  Invoicing, payments, recurring billing, expenses, and financial reports on Partners in Biz.
  **EFT-first, PayPal-second, no Stripe** (South Africa). Handles full invoice lifecycle (draft →
  sent → viewed → proof uploaded → paid), EFT banking details + proof-of-payment flow, PayPal fallback
  for international clients, recurring invoices, expense submission + approval + billing-to-client,
  and reports on revenue, outstanding aging, client lifetime value, and expense breakdowns. Use this
  skill whenever the user mentions anything financial, including: "create an invoice", "draft invoice",
  "send invoice", "invoice PDF", "duplicate invoice", "recurring invoice", "next invoice number",
  "EFT", "EFT details", "banking details", "payment instructions", "proof of payment", "POP",
  "upload POP", "confirm payment", "verify payment", "mark invoice paid", "PayPal invoice",
  "PayPal order", "PayPal capture", "PayPal payment link", "international payment", "overdue invoice",
  "invoice viewed", "follow up invoice", "log expense", "submit expense", "expense report",
  "approve expense", "reject expense", "reimburse expense", "bill expense to client",
  "revenue report", "monthly revenue", "quarterly revenue", "outstanding invoices", "aged receivables",
  "client lifetime value", "top clients", "expense by category", "VAT", "ZAR", "currency",
  "quote to invoice", "mark as paid", "invoice status", "FX rates", "exchange rates",
  "currency rates". If in doubt, trigger.
---

# Billing & Finance — Partners in Biz Platform API

Full invoicing + payments + recurring billing + expenses + financial reports. Designed for South African operations: **EFT is primary (zero fees), PayPal is secondary (international clients). No Stripe.**

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

Two public endpoints:
- `POST /invoices/[id]/mark-viewed?token=X` — invoice view tracking
- `POST /webhooks/paypal` — PayPal webhook receiver

## Payment philosophy

1. **EFT is preferred.** Banking details live on the platform owner org's `billingDetails.bankingDetails`. When an invoice is sent, the client receives a public link showing the banking details + a reference (invoice number). They pay via EFT, then upload proof of payment. Admin (or agent) verifies the proof and confirms → invoice moves to `paid`.

2. **PayPal is secondary.** Only active if `PAYPAL_CLIENT_ID` + `PAYPAL_CLIENT_SECRET` env vars are set. Used for international clients where EFT isn't practical. Flow: create PayPal order → client approves → capture → invoice paid.

3. **No Stripe** — deliberately not supported.

Required env vars for PayPal: `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_ENV` (`live` or `sandbox`), `PAYPAL_WEBHOOK_ID`, `PUBLIC_BASE_URL`.

## PiB-owned billing model

PiB-issued invoices and quotes are source/recipient records:

- `orgId`, `sourceOrgId`, and `issuerOrgId` are the sender/source workspace. For Partners in Biz billing, this is the resolved platform owner org (`type === 'platform_owner'`, normally `pib-platform-owner`).
- `billingOrgId` identifies the billing entity and is normally the same platform owner org for PiB-issued billing.
- `recipientOrgId` and `targetOrgId` are the client organization that receives the invoice or quote.
- `companyId` / `sourceCompanyId` point to the sender-owned CRM Company, normally the PiB platform CRM Company whose `linkedOrgId` is the client org.
- `contactId` / `sourceContactId` point to the sender-owned CRM Contact when the invoice or quote targets a specific contact.

Do not treat `allowedOrgIds` as client portal/CRM access. It scopes admin billing visibility only. Client users and explicit client members see received billing through `view=received`.

## Member-owned-client issuer (staff stay members)

Org owners/admins grant members explicit `capabilities.invoices` / `capabilities.quotes` on Team access. That grant does **not** come from `modules.billing` alone. Granted members create/list issuer invoices and quotes only for CRM **owned_or_linked** clients. Client-chat CRM companies/contacts remap onto `pib-platform-owner` the same way. See skill `pib-staff-billing-access`. Do not promote staff to Platform User admin solely to issue client invoices or edit their CRM book.

## Invoice status machine

```
draft ──► sent ──► viewed ──► payment_pending_verification ──► paid
              │                                        │
              └──► paid (PayPal immediate capture)     └──► sent (if rejected)
              │
              └──► overdue (cron flips after dueDate)
              │
              └──► cancelled
```

Any status → `cancelled`. `partially_paid` exists as a state but is rarely used.

## Collaboration primitives

- **Idempotency** on `POST /invoices`, `POST /quotes` (see `crm-sales`), and `POST /expenses`
- **Comments** (`resourceType: 'invoice' | 'expense'`): internal notes with `@mentions`
- **Notifications**: auto-created on `invoice.paid`, `invoice.overdue`, `expense.submitted`, proof uploads

---

## API Reference

### Invoices — CRUD

#### `GET /invoices` — auth: admin
List invoices. Supports source/recipient views.

- Default/sent view: `?orgId=X` filters by sender/source org.
- Received view: `?view=received&orgId=<clientOrgId>` filters by `recipientOrgId`.
- Platform billing view: `?view=received&billingOrgId=pib-platform-owner` lists PiB-issued invoices by recipient client. Super admins see all; restricted admins see only invoices whose `recipientOrgId` is in explicit `allowedOrgIds`.
- Shared view: `?view=shared` returns token/claim-backed rows without leaking unrelated org data.

Sorted `createdAt desc`, limit 50.

#### `POST /invoices` — auth: admin
Required: `orgId` (client org), `lineItems: [{ description, quantity, unitPrice }]`.

Body:
```json
{
  "orgId": "org_client",
  "recipientOrgId": "org_client",
  "companyId": "crm_company_id",
  "contactId": "crm_contact_id",
  "lineItems": [
    { "description": "Strategy session", "quantity": 2, "unitPrice": 2500 },
    { "description": "Implementation", "quantity": 1, "unitPrice": 15000 }
  ],
  "dueDate": "2026-05-01",
  "taxRate": 15,
  "currency": "ZAR",
  "notes": "Payment via EFT preferred — banking details on public invoice page."
}
```

For admin/AI PiB-issued invoices without CRM claim fields, `orgId` is the client/recipient org in the request; the API resolves the platform owner as `sourceOrgId` and writes `recipientOrgId=orgId`. For CRM-targeted invoices, pass `companyId`/`contactId` and optional `recipientOrgId`; if the Company already has `linkedOrgId`, the API reuses it.

PiB **staff members** (org role `member` on `pib-platform-owner`, not Platform User admin) chatting in a client company: POST `orgId` as the conversation/client org and pass the platform CRM `companyId` (or omit it and let the API resolve via `linkedOrgId`). The API remaps `sourceOrgId`/`issuerOrgId` to `pib-platform-owner` and treats the client org as recipient. Do **not** wait for Peet when that staff member asked for the invoice on their owned/linked book. Do not POST another staff member's company. From the Partners in Biz workspace, POST `orgId=pib-platform-owner` with the CRM company as usual.

Auto-snapshots:
- `fromDetails` from platform owner org (name, address, email, phone, vatNumber, bankingDetails)
- `clientDetails` from client org (`billingDetails`, `billingEmail`)
- Sequential `invoiceNumber` like `CLI-001` via `generateInvoiceNumber`
- `billingOrgId` — identifies the platform org issuing the invoice. Defaults to the `platform_owner` org. Override via `body.billingOrgId` when a workspace runs multiple billing entities. Reports use this to separate revenue per billing entity.
- `recipientOrgId` / `targetOrgId` — client org when known.
- `claimStatus` / `claimToken` — present when invoice is claimable from a CRM recipient.

Auto-computes: `subtotal`, `taxAmount`, `total`. Defaults currency from client org `settings.currency` or `USD`.

Response (201): `{ id, invoiceNumber }`. Dispatches `invoice.created`.

#### `GET /invoices/[id]` — auth: admin
Full invoice.

#### `PATCH /invoices/[id]` — auth: admin
Update fields. Recomputes totals if `lineItems` or `taxRate` changes.

#### `DELETE /invoices/[id]` — auth: admin
Soft-cancel (`status: 'cancelled'`).

#### `POST /invoices/preview` — auth: admin
Body: invoice-like JSON. Optional `orgId` enriches the preview with real client billing details and platform-owner sender details after access validation. Returns rendered invoice HTML and does not create a Firestore invoice. Useful before committing.

#### `GET /invoices/[id]/html` — auth: client+
Returns the same print-friendly invoice HTML used by the portal preview / Messages Context Dock. Prefer this after create so the human can review the document layout in chat.

#### `GET /invoices/next-number?orgId=X` — auth: admin
Returns the next invoice number for the client org: `{ invoiceNumber: "CLI-042" }`.

#### `GET /invoices/[id]/pdf` — auth: admin
Returns a PDF binary (Content-Type: application/pdf).

#### `POST /invoices/[id]/duplicate` — auth: admin
Clones the invoice as a new `draft`. Returns `{ id, invoiceNumber }`.

#### `POST /invoices/[id]/recurring` — auth: admin
Creates an active recurring schedule for this invoice. Body requires `interval` (`daily|weekly|monthly|quarterly|yearly`) and `startDate`; optional `endDate`. Fails with 409 if an active/paused schedule already exists.

#### `DELETE /invoices/[id]/recurring` — auth: admin
Cancels the active/paused recurring schedule for this invoice by setting `status: cancelled`.

### Invoice actions — send + status

#### `POST /invoices/[id]/send` — auth: admin
Generates `publicToken` if absent, sets `status: 'sent'`, `sentAt`. Emails `clientDetails.email` with the public view URL **and a PDF attachment**. Requires a client email. Returns `{ id, status, emailed, recipientEmail }`.

Dispatches `invoice.sent` webhook.

#### `POST /invoices/[id]/mark-viewed?token=X` — **public**
Called by the public invoice view page when loaded. Sets `firstViewedAt` (once), increments `viewCount`, auto-flips `status: 'sent' → 'viewed'`. 404 if token doesn't match.

### Invoice actions — payment

#### `GET /invoices/[id]/payment-instructions` — auth: admin OR `?token=<publicToken>`
Dual-auth. Either pass the admin `Authorization` header, or pass the invoice's `publicToken` as `?token=X`. The public invoice view page uses the token path.

Returns:
```json
{
  "invoiceNumber": "CLI-042",
  "total": 17250,
  "currency": "ZAR",
  "dueDate": "2026-05-01",
  "eft": {
    "bankingDetails": {
      "bankName": "FNB",
      "accountName": "Partners in Biz (Pty) Ltd",
      "accountNumber": "...",
      "branchCode": "...",
      "swift": "..."
    },
    "reference": "CLI-042",
    "proofOfPaymentEmail": "billing@partnersinbiz.online"
  },
  "paypal": { "available": true, "url": "<BASE>/api/v1/invoices/inv_xyz/paypal-order" },
  "publicViewUrl": "https://partnersinbiz.online/invoice/<publicToken>"
}
```

Generates `publicToken` if missing. `paypal.available: true` only if `PAYPAL_CLIENT_ID` set.

#### `POST /invoices/[id]/payment-proof` — auth: admin (or client portal)
Client uploaded proof of payment. Body: `{ fileId: string, note?: string }`.

Updates: `status: 'payment_pending_verification'`, `paymentProofFileId`, `paymentProofUploadedAt`. Creates org-wide notification for platform admins.

#### `POST /invoices/[id]/confirm-payment` — auth: admin
Admin verifies the uploaded proof.

Body to confirm:
```json
{ "confirmed": true, "paymentMethod": "eft", "reference": "...", "amount": 17250 }
```

Body to reject:
```json
{ "confirmed": false, "reason": "Amount doesn't match invoice total" }
```

- Confirmed: `status: 'paid'`, `paidAt`, `paymentMethod`, `paymentReference`, `paidAmount`. Dispatches `invoice.paid` + `payment.received`. Notifies invoice creator.
- Rejected: `status: 'sent'` (reverts), `paymentProofRejectedReason`, `paymentProofRejectedAt`. Notifies proof uploader.

#### `PATCH /invoices/[id]/mark-paid` — auth: admin
Manual mark-paid (no proof flow). Body:
```json
{ "paymentMethod": "eft" | "paypal" | "cash" | "card" | "other",
  "paidAt": "2026-04-15T...", "reference": "...", "amount": 17250, "proofFileId": "..." }
```

Required: `paymentMethod`. Dispatches `invoice.paid` + `payment.received`. Creates an `activities` entry and notifies invoice creator.

### PayPal

All three require `PAYPAL_CLIENT_ID` + `PAYPAL_CLIENT_SECRET`. Return `503 "PayPal is not configured"` otherwise.

#### `POST /invoices/[id]/paypal-order` — auth: admin
Creates a PayPal order (intent: CAPTURE). Returns:
```json
{ "orderId": "PAY-...", "approveUrl": "https://...", "provider": "paypal" }
```

Stores `paypalOrderId` on invoice.

#### `POST /invoices/[id]/paypal-capture` — auth: admin
Captures the order. Body: `{ orderId: string }` — must match stored order. Marks invoice paid with `paymentMethod: 'paypal'`, `paymentReference: captureId`. Dispatches `invoice.paid` + `payment.received`.

#### `POST /webhooks/paypal` — **public**
PayPal webhook receiver. Verifies signature via PayPal's verify endpoint (requires `PAYPAL_WEBHOOK_ID`). Handles:
- `CHECKOUT.ORDER.APPROVED`
- `PAYMENT.CAPTURE.COMPLETED`

Always returns 200 (prevents PayPal retries). Logs failures.

### Recurring schedules

#### `GET /recurring-schedules` — auth: admin
Lists up to 100 schedules, ordered newest first. Query: `status` (`active` by default, or `all`). Restricted admins are filtered to explicit allowed orgs.

#### `PATCH /recurring-schedules/[id]` — auth: admin
Body:
```json
{ "status": "active" | "paused" | "cancelled" }
```

Cannot update a schedule already marked `cancelled`. Create/cancel schedules from the invoice-owned route: `POST /invoices/[id]/recurring` and `DELETE /invoices/[id]/recurring`.

The daily cron `/api/cron/invoices` runs at 2am UTC and generates invoices from active schedules whose `nextDueAt <= now`.

### Expenses

#### `GET /expenses` — auth: admin
Filters: `orgId` (required), `userId`, `status`, `category`, `projectId`, `clientOrgId`, `from`, `to`, `billable`, `billed` (has invoiceId), `page`, `limit`.

#### `POST /expenses` — auth: admin (idempotent)
Required: `date`, `amount`, `category`. Defaults: `currency='ZAR'`, `billable=false`, `reimbursable=true`, `status='draft'`, `userId=current user`.

Body:
```json
{
  "orgId": "org_abc",
  "date": "2026-04-10",
  "amount": 450,
  "currency": "ZAR",
  "category": "travel",
  "description": "Uber to client meeting",
  "vendor": "Uber",
  "receiptFileId": "file_xyz",
  "projectId": "proj_abc",
  "clientOrgId": "org_client",
  "billable": true,
  "reimbursable": true
}
```

#### `GET/PUT/DELETE /expenses/[id]` — auth: admin
PUT rejects if status is `approved`/`reimbursed`/`rejected` OR `invoiceId` is set (409).

#### `POST /expenses/[id]/submit` — auth: admin
`draft → submitted`. Creates org-wide notification. Dispatches `expense.submitted`.

#### `POST /expenses/[id]/approve` — auth: admin
Body: `{ action: 'approve' | 'reject', note?: string }`.
- `approve`: `status: 'approved'`, `reviewedBy`, `reviewedAt`. Notifies submitter.
- `reject`: `status: 'rejected'`, `rejectionReason=note`, notify submitter.

Requires current status `submitted` (409 otherwise).

#### `POST /expenses/bill` — auth: admin
Bill approved billable expenses to a client invoice.

Body: `{ expenseIds: string[], invoiceId: string }`.

Each expense becomes an invoice line item `{ description: "<category>[: <description>]", quantity: 1, unitPrice: amount, amount }`. Recomputes invoice totals. Sets `invoiceId` on each expense. Batched atomically.

Response: `{ billed: count, invoiceId, newTotal }`.

### Reports (billing-related)

See the `reports` skill for full request/response shapes. Quick reference for billing agents:

- `GET /reports/revenue?orgId=X&from=...&to=...&groupBy=month` — paid invoices bucketed by `paidAt`.
- `GET /reports/outstanding?orgId=X` — aged receivables (`sent`/`overdue`/`payment_pending_verification`) by `dueDate` age bucket.
- `GET /reports/client-value?orgId=X` — top clients ranked by lifetime paid total.
- `GET /reports/expense-summary?orgId=X&from=...&to=...&groupBy=category|project|user` — expense breakdown.

### Comments on invoices/expenses

```json
POST /comments
{ "orgId": "org_abc", "resourceType": "invoice", "resourceId": "inv_xyz",
  "body": "Client asked to extend due date by 14 days. @user:uid123 please confirm." }
```

### FX rates

#### `GET /fx/rates` — auth: public (no API key required)

Returns cached FX-to-ZAR rates for a given date. Rates are not sensitive and are readable without authentication — see `## Auth (mandatory)` above for how this differs from every other route in this skill.

Query:
- `date` (optional, `YYYY-MM-DD`) — defaults to today.

Response:
```json
{
  "ok": true,
  "date": "2026-05-07",
  "base": "ZAR",
  "source": "...",
  "rates": {
    "USD": 18.45,
    "EUR": 19.82,
    "GBP": 23.10
  }
}
```

`rates` maps currency codes to their value in the base currency (ZAR). Rates are pre-fetched and cached — this endpoint reads the cache, it does not trigger a live fetch.

Error (400): `date must be YYYY-MM-DD`.
Error (500): cache miss or upstream fetch failure.

```bash
# Convert an invoice amount to ZAR
GET /fx/rates
# → { rates: { USD: 18.45, EUR: 19.82 } }
# Multiply invoice.total by rates[invoice.currency]
# e.g. USD 1000 * 18.45 = ZAR 18,450
```

---

## Workflow guides

### 1. EFT payment flow (primary path)

```bash
# 1. Create invoice
POST /invoices
{ "orgId": "org_client", "lineItems": [...], "dueDate": "2026-05-01", "taxRate": 15, "currency": "ZAR" }
# → { id: "inv_xyz", invoiceNumber: "CLI-042" }

# 2. Send it
POST /invoices/inv_xyz/send
# Emails client with public view URL + PDF. Status: sent. Dispatches invoice.sent

# 3. Client views the public invoice page
# (public GET triggers) POST /invoices/inv_xyz/mark-viewed?token=<publicToken>
# Status remains 'sent' but viewedAt/viewCount populate. If first view, status flips to 'viewed'.

# 4. Get payment instructions (to show on public page)
GET /invoices/inv_xyz/payment-instructions
# Returns EFT banking details + reference + publicViewUrl

# 5. Client pays via EFT, uploads proof
POST /invoices/inv_xyz/payment-proof
{ "fileId": "upload_file_id_from_upload_endpoint", "note": "Paid via EFT 15 Apr" }
# Status: payment_pending_verification. Admin gets notification.

# 6. Admin verifies proof
POST /invoices/inv_xyz/confirm-payment
{ "confirmed": true, "paymentMethod": "eft", "reference": "CLI-042", "amount": 17250 }
# Status: paid. Dispatches invoice.paid + payment.received.
```

### 2. PayPal flow (international)

```bash
POST /invoices/inv_xyz/send   # same
# Public invoice page shows PayPal button if available

POST /invoices/inv_xyz/paypal-order
# → { orderId: "PAY-...", approveUrl: "https://..." }
# Redirect client to approveUrl

# After client approves on PayPal:
POST /invoices/inv_xyz/paypal-capture
{ "orderId": "PAY-..." }
# Captures + marks paid.

# OR the webhook path:
# PayPal POSTs to /webhooks/paypal with CHECKOUT.ORDER.APPROVED or PAYMENT.CAPTURE.COMPLETED
# → automatically marks paid
```

### 3. Recurring monthly invoice

```bash
# Create the template invoice first (keep it in draft)
POST /invoices
{ "orgId": "org_client", "lineItems": [{ "description": "Monthly retainer", "quantity": 1,
  "unitPrice": 15000 }], "taxRate": 15, "currency": "ZAR" }

POST /invoices/inv_template/recurring
{ "interval": "monthly", "startDate": "2026-05-01" }

# Daily cron generates the new invoice at 2am UTC on the schedule
```

### 4. Submit and approve an expense

```bash
POST /expenses
{ "orgId": "org_abc", "date": "2026-04-10", "amount": 450, "currency": "ZAR",
  "category": "travel", "description": "Client meeting", "billable": true,
  "clientOrgId": "org_client", "receiptFileId": "file_xyz" }

POST /expenses/exp_abc/submit   # draft → submitted

POST /expenses/exp_abc/approve
{ "action": "approve" }   # status → approved
```

### 5. Bill billable expenses to a client invoice

```bash
# Create a new invoice or use existing
POST /expenses/bill
{ "expenseIds": ["exp_abc", "exp_def"], "invoiceId": "inv_xyz" }
# Appends line items, recomputes totals, marks expenses billed
```

### 6. Handle overdue invoices

```bash
# Cron /api/cron/invoices runs daily at 2am UTC
# For each invoice where status in ['sent','viewed','payment_pending_verification']
# AND dueDate < now: sets status='overdue', markedOverdueAt, dispatches invoice.overdue

# Check aged receivables
GET /reports/outstanding?orgId=org_abc
```

### 7. Revenue reports

```bash
GET /reports/revenue?orgId=org_abc&from=2026-01-01&to=2026-04-16&groupBy=month
GET /reports/client-value?orgId=org_abc
```

### 8. PiB platform billing views

```bash
# Partners in Biz admin billing page: PiB is sender, clients are recipients.
GET /invoices?view=received&billingOrgId=pib-platform-owner

# A specific client org's received invoice list.
GET /invoices?view=received&orgId=org_client

# Client portal billing tab.
GET /invoices?view=received
GET /quotes?view=received
```

## Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `orgId is required` | Include orgId in body |
| 400 | `At least one line item is required` | Add line items |
| 400 | `Invalid payment method` | Use `eft`/`paypal`/`cash`/`card`/`other` |
| 400 | `Can only approve/reject a submitted expense` | Check status first |
| 404 | `Invoice not found` / `Client organisation not found` | Verify IDs |
| 409 | `Cannot modify a billed entry` / `Cannot delete a billed expense` | Unlink invoice first |
| 503 | `PayPal is not configured` | Set `PAYPAL_CLIENT_ID` + `PAYPAL_CLIENT_SECRET` |

## Messages side-canvas handoff

When the run happens inside Messages, after `POST /invoices` (or after a meaningful draft update the human should review), emit a web-native `uiActions` entry so Messages attaches the invoice and opens the Context Dock with the real document HTML preview:

```json
{
  "id": "open-invoice",
  "type": "open_context",
  "label": "Preview invoice",
  "payload": { "kind": "invoice", "id": "<invoiceId>", "label": "<invoiceNumber>" }
}
```

Messages treats `open_context` with `{ kind: "invoice", id }` as attach-and-open. The Context Dock renders the print-friendly invoice layout (same HTML as the portal preview) with **Download PDF** and **Send email** (PDF attachment to the client email). Still include the admin/portal invoice URL in the message text. Do **not** auto-send; wait for human review before `POST /invoices/[id]/send` (or use the dock Send button).

For dry-run totals before create, still use `POST /invoices/preview`. Once the invoice exists, prefer `open_context` over pasting raw HTML.

## Agent patterns

1. **Always prefer EFT** — it's cheaper. Only suggest PayPal when client is international.
2. **Check `payment-instructions` before sending** — confirms banking details are populated on the platform org.
3. **Verify proof of payment carefully** — confirm amount + reference match the invoice before confirming.
4. **Use `/invoices/preview` before committing** — lets you show the user the totals first.
5. **After create in Messages, emit `open_context`** — so the human sees the invoice layout in the side canvas before send.
6. **Idempotency on creates** — pass `Idempotency-Key: <uuid>` on `POST /invoices` and `POST /expenses`.
7. **Webhooks** — subscribe to `invoice.paid`, `invoice.overdue`, `payment.received` (see `platform-ops`).
8. **Currency consistency** — check client org `settings.currency`; default to `ZAR` for SA clients.
9. **PiB-issued resources** — keep PiB as source/issuer and clients as recipients. For Partners in Biz billing pages, query received invoices by `billingOrgId=pib-platform-owner`, not `orgId=pib-platform-owner`.
