# User-delegation and device OAuth

Interactive agents may only perform actions the **requesting human** could perform in the portal.

| Actor | Credential |
| --- | --- |
| Human in Messages | Session → mint `pib_dlg_` (automatic) |
| External Cursor / Claude / Hermes | Device OAuth (`pib-skills login`) or Settings personal token (`pib_usr_`) |
| Cron / watcher | `AI_API_KEY` or `pib_ag_` / `pib_ak_` |

## Device login

1. `POST /api/v1/oauth/device/code`
2. Human opens `/connect/agent?code=ABCD-EFGH` and approves one org
3. `POST /api/v1/oauth/token` with `grant_type=urn:ietf:params:oauth:grant-type:device_code`
4. `GET /api/v1/oauth/whoami` with the access token

Access tokens are `pib_dlg_` (1 hour). Refresh tokens are `pib_rt_` (~30 days).

## Personal tokens

Settings → Connected agents mints `pib_usr_`. Same acting-user path as device OAuth. Workspace API keys remain system keys and are the wrong product for “act as me”.
