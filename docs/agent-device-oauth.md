# Agent device OAuth

External agents (Cursor, Claude Code, Hermes outside Messages) prove **which human** they act as with RFC 8628 device login. They do not use workspace API keys (`pib_ak_`) or the platform `AI_API_KEY`.

## Flow

1. `./bin/pib-skills login` → `POST /api/v1/oauth/device/code`
2. Open `/connect/agent?code=XXXX-XXXX`, sign in, pick a workspace, approve
3. Poll `POST /api/v1/oauth/token` with `grant_type=urn:ietf:params:oauth:grant-type:device_code`
4. Store `access_token` (`pib_dlg_…`, 1 hour) and `refresh_token` (`pib_rt_…`, 30 days)
5. `GET /api/v1/oauth/whoami` then send `Authorization` + `X-Org-Id` on `/api/v1/*`

Headless fallback: Settings → Connected agents → Create personal token (`pib_usr_…`). Same acting-user resolution.

## Rules

- Access tokens resolve as the human (`authKind: user_delegation`). Org ACLs and module policy apply.
- Admin/ops skills are public docs. APIs still 403 when membership cannot do the action.
- Revoke from Settings → Connected agents, or `POST /api/v1/oauth/revoke`.
- Workspace API keys remain cron/integration credentials. They act as `role: ai`, not as you.
