---
name: system-auth
description: >
  Authenticate Partners in Biz API calls correctly. Interactive agent work must use a
  user-delegation token scoped to the requesting human's org/module access. External
  agents (Cursor, Claude Code, Hermes outside Messages) must run pib-skills login or
  use a Settings personal token. Platform AI_API_KEY / long-lived agent keys are for
  cron and system jobs only. Use whenever an agent is about to call /api/v1/*.
---

# System Auth — Partners in Biz

## Rules (non-negotiable)

1. **Interactive work acting for a human** → user-delegation token (`pib_dlg_…`) or personal token (`pib_usr_…`).
2. **Cron, watchers, system maintenance** → platform `AI_API_KEY` or per-agent `pib_ag_` / workspace `pib_ak_` keys only.
3. Skills describe *how* to call the API. The API enforces *whether*. Never assume a god-key bypasses org ACLs.
4. Effective permission = `user scopes ∩ agent capability ∩ approval gates`.
5. After login, call `GET /api/v1/oauth/whoami` and send `X-Org-Id` on every tenant call.
6. On 403, print the API `error` and stop. Do not retry with `AI_API_KEY`.

## Mode A — Messages / in-app chat (automatic)

When a human sends a Messages chat that dispatches Hermes / linked-computer runs, the platform mints a **fresh** short-lived delegation on **every turn** and injects:

```
[Partners in Biz API auth — user delegation]
Authorization: Bearer pib_dlg_…
X-Org-Id: <orgId>
```

Prefer that injected Bearer token for all `/api/v1/*` calls in the run. Do not fall back to `AI_API_KEY`.

If `/api/v1/agent/email/*` returns 401/403, the platform remints once in the same run and retries silently. Do not ask the human to send another chat message.

## Mode B — External agents (Cursor, Claude Code, your Hermes)

You do not have a Messages-injected token. Identify the human first.

```bash
./bin/pib-skills login
./bin/pib-skills whoami
```

`login` starts device OAuth, opens `https://partnersinbiz.online/connect/agent`, and stores credentials at `~/.config/partnersinbiz/credentials.json`.

Headless fallback (Settings → Connected agents → Create personal token):

```bash
export PIB_ACCESS_TOKEN='pib_usr_…'
export PIB_ORG_ID='<orgId>'
```

Then:

```http
GET /api/v1/oauth/whoami
Authorization: Bearer <token>
X-Org-Id: <orgId>
```

Use the returned `uid`, `email`, `orgId`, `memberRole` as the acting identity. Admin/ops skills still 403 when `memberRole` cannot perform the action.

```http
Authorization: Bearer <pib_dlg_ or pib_usr_>
X-Org-Id: <orgId>
```

Refresh: `POST /api/v1/oauth/token` with `{ "grant_type": "refresh_token", "refresh_token": "pib_rt_…" }`. `pib-skills whoami` refreshes automatically.

Workspace API keys on Settings → API keys (`pib_ak_`) act as a **system agent**, not as the human. Do not use them for interactive agent work.

## Interactive mint (in-app sessions only)

```http
POST /api/v1/agent/delegations
Authorization: Bearer <user_session_or_id_token>
```

External agents should use device login instead of this route.

## System auth (cron only)

```http
Authorization: Bearer <AI_API_KEY_or_agent_key>
X-Org-Id: <orgId>
```

Tag writes with `createdByType: "system"` when the job is cron-originated.

## Forbidden

- Using the platform god-key in an interactive session “because it is easier”
- Creating resources in an org the requesting user cannot access
- Claiming success after a write without read-back
- Inventing a remint ritual for the human to paste a new token into chat

## When access is denied

Surface the exact API `error` string. Ask the human to grant access, switch workspace, or re-run `pib-skills login`. Never retry with a more privileged key.
