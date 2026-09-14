---
name: platform-admin-users
description: >
  Platform Users super-admin staff management on Partners in Biz: list/create/update/delete
  PiB internal staff accounts (role === 'admin'), the allowedOrgIds restricted-vs-super-admin
  scoping model, welcome-email/setup-link onboarding, and staff offboarding. Restricted to
  super admins only. Owner: pip. Critical risk — this skill creates/deletes login-capable
  staff accounts and controls org-wide admin visibility. Use this skill whenever the user
  mentions: "platform users", "add staff", "invite admin", "new admin account",
  "super admin", "restrict admin access", "allowedOrgIds", "promote to super admin",
  "offboard staff", "remove admin access", "reset admin password", "staff welcome email",
  "setup link", "platform staff". If in doubt, trigger.
---

# Platform Admin Users — Partners in Biz Platform API

Manages PiB **internal staff** (users with `role === 'admin'`). Restricted to **super admins
only** — an admin whose `allowedOrgIds` array is empty. A restricted admin (non-empty
`allowedOrgIds`) cannot call these endpoints; this prevents silent self-elevation.

## Related skills

- `agent-runtime-ops` — Hermes agent registry/admin (different from platform staff users)
- `platform-ops` — general platform primitives
- `system-auth` — auth/delegation mint & resolve rules

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

- Call `GET /api/v1/oauth/whoami` first. If `memberRole` is not owner/admin (or super-admin for staff routes), say so and stop. On 403 print the API `error` — do not retry with `AI_API_KEY`.

## Base URL & Authentication

```
https://partnersinbiz.online/api/v1
```

```
Authorization: Bearer <AI_API_KEY>
```

All routes below additionally require the caller to be a **super admin** (`allowedOrgIds: []`).

## User model

```json
{
  "uid": "firebase_uid",
  "email": "staff@partnersinbiz.online",
  "displayName": "Alice Smith",
  "role": "admin",
  "orgId": "PIB_PLATFORM_ORG_ID",
  "allowedOrgIds": ["org_abc", "org_xyz"],
  "isSuperAdmin": false,
  "createdAt": "...",
  "updatedAt": "..."
}
```

`isSuperAdmin` is a derived field: `true` when `allowedOrgIds.length === 0`. It is never stored; it is computed on every read.

## `allowedOrgIds` scoping concept

- **Super admin** — `allowedOrgIds: []` (empty). Sees and manages every org on the platform.
- **Restricted admin** — `allowedOrgIds: ["org_a", "org_b"]`. UI and API scope them to those orgs only.
- To convert a restricted admin to super admin, PATCH with `allowedOrgIds: []`.
- A super admin **cannot restrict their own account** via PATCH — they must ask a different super admin. This prevents accidental self-lockout.
- `allowedOrgIds` is admin-surface visibility only. It does not grant client portal/CRM access. To let a PiB admin enter a client portal, add the staff user as an explicit member of that client org through `/admin/org/[slug]/team` or `POST /organizations/[id]/members`.
- For `/admin/org/partners-in-biz/billing`, restricted admins see only PiB-issued invoices where the recipient client is inside `allowedOrgIds`; super admins see all PiB-issued invoices.

## API Reference

### `GET /admin/platform-users` — auth: super-admin

Lists all users with `role === 'admin'`, sorted newest first.

Response:
```json
[
  { "uid": "...", "email": "...", "displayName": "...", "role": "admin",
    "orgId": "...", "allowedOrgIds": ["org_abc"], "isSuperAdmin": false,
    "createdAt": "...", "updatedAt": "..." }
]
```

### `POST /admin/platform-users` — auth: super-admin

Creates a new platform staff account. Finds or creates the Firebase Auth user, writes the `users` doc, then optionally sends a welcome email with a password-setup link.

Body:
```json
{
  "email": "newstaff@example.com",
  "name": "Bob Jones",
  "allowedOrgIds": ["org_abc"],
  "sendWelcomeEmail": true
}
```

- `allowedOrgIds` — omit or pass `[]` for a super admin; pass org IDs to restrict.
- `sendWelcomeEmail` — defaults to `true`. Sends a branded email from the platform address with a Firebase password-reset link so the new user can set their own password.
- If a user with this email already exists as a **non-admin** role (e.g. `member`), returns `409` — resolve in the team page first.

Response (201):
```json
{
  "uid": "...", "email": "...", "displayName": "...", "role": "admin",
  "orgId": "PIB_PLATFORM_ORG_ID", "allowedOrgIds": [],
  "isSuperAdmin": true,
  "setupLink": "https://..."
}
```

`setupLink` is the Firebase password-reset URL returned once at creation. Store or send it immediately — it is not re-exposed later.

### `GET /admin/platform-users/[uid]` — auth: super-admin

Returns a single platform admin by UID. Returns `404` if the UID exists but is not an admin.

### `PATCH /admin/platform-users/[uid]` — auth: super-admin

Updatable fields:
- `name` — updates both Firestore `displayName` and Firebase Auth display name. Cannot be empty string.
- `allowedOrgIds` — replaces the full list. Pass `[]` to promote to super admin. Deduplication and trimming applied automatically.

Self-restriction guardrail: if `uid === caller.uid` and `allowedOrgIds` is non-empty, returns `400` — ask another super admin to do it.

Response: updated user object.

### `DELETE /admin/platform-users/[uid]` — auth: super-admin

Deletes the Firebase Auth user (revokes all sessions) and removes the Firestore `users` doc. Cannot delete yourself — returns `400`.

Response: `{ "uid": "...", "deleted": true }`.

### Password / reset utility routes

| Method | Path | Auth | Use |
|---|---|---|---|
| PATCH | `/admin/platform-members/[uid]/password` | super-admin | Set/reset platform member password. |
| POST | `/admin/platform-members/[uid]/reset` | super-admin | Send/reset platform member access. |
| PATCH | `/admin/platform-users/[uid]/password` | super-admin | Set/reset platform user password. |
| POST | `/admin/platform-users/[uid]/reset` | super-admin | Send/reset platform user access. |

`platform-members` and `platform-users` are the same underlying staff-account concept exposed through two route families — use whichever the calling surface (admin UI page) already targets; both require super-admin.

## Workflow: onboard a new staff member

```bash
# 1. Create the account (welcome email sent automatically)
POST /admin/platform-users
{ "email": "alice@example.com", "name": "Alice Smith",
  "allowedOrgIds": ["org_client1", "org_client2"] }
# → { uid, setupLink }

# 2. If the email failed or they need a new link, use Firebase Console
#    or re-POST with sendWelcomeEmail: true (idempotent — merges the doc)

# 3. Promote to super admin later
PATCH /admin/platform-users/<uid>
{ "allowedOrgIds": [] }

# 4. Off-board
DELETE /admin/platform-users/<uid>
```

## Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `name cannot be empty` | Provide a non-empty `name` on PATCH |
| 400 | Self-restriction blocked | Ask a different super admin to restrict this account |
| 400 | Self-delete blocked | Cannot delete your own account |
| 403 | Forbidden | Caller is a restricted admin, not a super admin |
| 409 | Email already exists as non-admin role | Resolve via the team page first |
| 404 | Not an admin | UID exists but `role !== 'admin'` |

## Agent patterns

1. **Verify super-admin status before attempting any write** — a 403 here means the caller lacks authority, not that the resource is missing.
2. **Always read back after create/patch/delete** to confirm the staff record matches what was requested.
3. **Never invent `allowedOrgIds` values** — resolve real org IDs first (see `client-manager`).
4. **Treat `setupLink` as one-time-sensitive** — store/send immediately, do not log it long-term.
5. **Distinguish this from `agent-runtime-ops`** — platform users are human staff logins; agents/Hermes profiles are a separate registry.
