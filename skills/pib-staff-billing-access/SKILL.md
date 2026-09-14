---
name: pib-staff-billing-access
description: >
  Use when a Partners staff member (role=member, not Platform User admin) needs to
  create or list PiB-issued invoices/quotes for owned CRM clients, or when org
  owners/admins grant invoice/quote issuer rights on Team access.
---

# PiB staff billing access (member-owned-client issuer)

## Product rule (approved 2026-08-03)

1. Staff stay `role=member` on Partners in Biz. Do **not** promote to Platform User admin just to issue invoices.
2. Each org **owner/admin** grants which **members** may issue **invoices** and/or **quotes** (Team access policy capabilities).
3. Grant is necessary but not sufficient: create/list still fail closed to CRM **owned_or_linked** clients for ordinary members.
4. Members never see the full issuer book of other staff clients.
5. Draft edit stays admin/AI or creator-while-draft; sent bill-to locks (SAA-001 class) stay locked.
6. Super admin + restricted Platform User `allowedOrgIds` paths stay unchanged.
7. Client-org owner/admin book (e.g. Humanaut AI owner) stays unchanged via `canManageOrgAs`.

## Capabilities vs modules

| Control | Meaning |
|---|---|
| `modules.billing` | Opens billing UI surfaces |
| `capabilities.invoices` | May create/list **issuer** invoices (still CRM-scoped) |
| `capabilities.quotes` | May create/list **issuer** quotes (still CRM-scoped) |

Billing module alone does **not** grant issuer rights.

Policy shape (`MemberAccessPolicy`):

```json
{
  "preset": "custom",
  "modules": { "crm": true, "billing": true },
  "recordScopes": { "crm": "owned_or_linked", "projects": "owned_or_linked" },
  "capabilities": { "invoices": true, "quotes": true }
}
```

Full workspace access (`FULL_ACCESS_POLICY`) implies both capabilities.

## Who can issue

| Actor | Path |
|---|---|
| Platform super admin / AI | Existing platform-issued + CRM claimable paths |
| Restricted platform admin | Same, scoped by `allowedOrgIds` / `canAccessOrg` |
| Org owner/admin | Full org book via `canManageOrgAs` (Humanaut owner book) |
| Org member + grant + owned CRM client | Create/list only for owned_or_linked clients |
| Org member + grant off | No issuer create; empty issuer/sent list |
| Org member + grant + other staff client | 403 / not listed |

## API behaviour

### Invoices `POST /api/v1/invoices`

- Platform admin/AI without CRM target: platform-issued (`sourceOrgId=pib-platform-owner`, `orgId`=client).
- Member with grant from the **Partners in Biz** workspace: supply CRM `companyId` and/or `contactId` owned/linked to them; `orgId` is the issuer workspace (`pib-platform-owner`).
- Member with grant from a **client company chat**: POST `orgId` as the conversation/client org (Messages already sends that `X-Org-Id`). The API remaps issuer to `pib-platform-owner` and recipient to the client org, then evaluates grant + `owned_or_linked` on the PiB membership. ELE-004 class: posting `orgId=<client>` is correct; do not wait for Peet.
- Owner/admin of client org: may still create that org's own book without CRM target.

### CRM companies and contacts

PiB staff CRM rows live on `pib-platform-owner`. Client-chat `X-Org-Id` is conversation context, not the CRM tenant. `withCrmAuth` remaps PiB staff onto the platform org; `owned_or_linked` still hides other staff’s book. Creates stamp `linkedOrgId` to the client workspace. Do not promote staff to Platform User admin for company/contact access.

### Quotes `POST /api/v1/quotes`

Same grant + owned_or_linked model. Agents/system and org owner/admin unchanged.

### List sent/issuer (`GET` default view)

- Without grant: empty issuer book for members.
- With grant: filtered by CRM owned_or_linked (existing billing CRM scope helpers).
- Received view (`view=received`) unchanged for payers.

## UI

Portal **Settings → Team → Edit access**:

- Toggles: **Invoices (owned/linked clients)** and **Quotes (owned/linked clients)**
- Copy explains rights apply only to clients the member owns or is linked to.

## Code anchors

- `lib/orgMembers/access-policy.ts` — `capabilities`, `memberCanIssueInvoices` / `memberCanIssueQuotes`
- `lib/billing/staff-issuer-remap.ts` — client-chat → platform issuer remap
- `lib/auth/crm-middleware.ts` — PiB staff CRM remap onto `pib-platform-owner`
- `lib/orgMembers/platform-staff.ts` — PiB staff membership + specialist grant merge
- `lib/billing/member-issuer.ts` — grant + owned-client gates
- `app/api/v1/invoices/route.ts`, `app/api/v1/quotes/route.ts`
- `app/(portal)/portal/settings/team/page.tsx`
- Tests: `__tests__/lib/billing/member-issuer.test.ts`, `__tests__/api/invoices.test.ts`

## Agent guidance

- Prefer granting Team capabilities for Stean-shaped staff; do not solve with Platform Users admin promotion.
- When creating invoices/quotes as a granted member, always pass CRM company/contact on the issuer org.
- Restricted Platform User + `allowedOrgIds` remains valid for multi-client admin staff who should see full books for those orgs — different product track from member-owned issuer.
- Draft/sent edit locks unchanged (`lib/invoices/permissions.ts`, `lib/billing/portal-permissions.ts`).

## Spec

Client document `cPjjOpkDh0fxMPusPJzX` — Member-owned-client PiB invoice issuer access model (Peet approved 2026-08-03).
