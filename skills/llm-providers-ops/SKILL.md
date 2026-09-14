---
name: llm-providers-ops
description: >
  Partners in Biz LLM provider connections: bring-your-own-provider credential connections,
  OAuth/device-code linking (xAI Grok, OpenAI Codex), and Hermes VPS/agent credential sync.
  Owner: theo. Use this skill whenever the user mentions connecting an LLM provider, provider
  OAuth, or per-org/per-agent model provider credentials.
---

# LLM Providers Ops — Partners in Biz Platform API

## Owner & scope

- Owner: `theo`
- Allowed: `theo` (all routes); any authenticated org member can list/read; only org admins (`canWriteOrgLlmConnection`) can write `scope: "org"` connections; agents (`user.role === 'ai'`) cannot start OAuth flows or create user-scoped connections
- Risk: high — writes/syncs credentials to Hermes profiles (org VPS and/or the caller's linked computers)
- Base path: `https://partnersinbiz.online/api/v1/llm-providers`
- Related: `system-auth`, `platform-ops`, `agent-runtime-ops`

Every connection is `scope: "org"` (syncs to the org's VPS Hermes profiles, shared by everyone using that VPS) or `scope: "user"` (syncs to the caller's linked computers; also to the org VPS when Team access `allowPersonalLlmOnOrgVps` is enabled — skipped when an org connection already covers that provider).

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Route map (shipped)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/llm-providers/connections?orgId=` | List available provider definitions, the org/caller's existing connections, and VPS sync-target info (`orgVpsDeviceCount`, `hasHermesProfileLink`, `reasonIfEmpty`) |
| POST | `/llm-providers/connections` | Create/upsert a credential connection. Body: `{ provider, scope: "org"\|"user", label?, credentials, sync?: boolean, agentIds? }`. Validates credentials live against the provider before saving (`validateLlmCredentials`); OAuth-only providers 400 here and must use `/oauth/start` instead. User-scope connections sync to the caller's linked computers (and org VPS when Team access allows); org-scope connections sync to VPS targets unless `sync: false` |
| DELETE | `/llm-providers/connections/[id]` | Revoke a connection. For connections already synced to agents, best-effort unsets the provider's env var or deletes the OAuth-token provider on each synced agent before revoking the Firestore record |
| POST | `/llm-providers/connections/[id]` | Re-sync an existing connection to its Hermes targets (optionally a specific `agentIds` list) |
| POST | `/llm-providers/oauth/start` | Start a device-code OAuth flow for an OAuth-capable provider (currently `xai-oauth`, `openai-codex`; anything else 400s pointing at `hermes auth add <provider>` on the VPS instead). Returns a `session` with `userCode`/`verificationUri` to show the human. Agents cannot call this (403) |
| GET | `/llm-providers/oauth/[sessionId]?orgId=` | Poll an OAuth session. Returns `pending: true` while the human hasn't approved the device code yet; on success upserts the connection (`authKind: "oauth_token"`), triggers a VPS sync, and marks the session `completed` |

## Agent patterns

### Connect an API-key provider and confirm it synced
1. `POST /llm-providers/connections` with `{ orgId, provider, scope: "org", credentials: { apiKey: "..." } }`.
2. Response includes `connection` and `sync` (`{ synced: [...], failed: [...] }`) — check `sync.failed` before reporting success; a partial sync is not a full success.
3. `GET /llm-providers/connections?orgId=...` and confirm the new connection id appears in `connections` with the expected `provider`/`scope` before telling the human it's connected.

### Device-code OAuth (xAI / Codex) end to end
1. `POST /llm-providers/oauth/start` with `{ orgId, provider: "xai-oauth" | "openai-codex", scope }` → show the human `session.userCode` + `session.verificationUri`.
2. Poll `GET /llm-providers/oauth/[sessionId]?orgId=...` on the session's `intervalSeconds` cadence. Treat `pending: true` as "keep polling," `status: "failed"`/`"expired"` as a hard stop to report, and `status: "completed"` (with a `connection`) as done.
3. After completion, `GET /llm-providers/connections?orgId=...` to read back the connection and confirm `sync.failed` is empty.

### Disconnect
`DELETE /llm-providers/connections/[id]?orgId=...` then `GET /llm-providers/connections?orgId=...` to confirm the id no longer appears (or appears revoked) before reporting removal — the delete path itself does best-effort agent cleanup that can partially fail without erroring the whole request.

## Success gate

After any create/sync/delete above:
1. `GET /llm-providers/connections?orgId=...` (or poll the OAuth session) to read back current state.
2. Assert the connection id, `scope`, and sync result match what was requested — a `sync.failed` entry means the human needs to know a specific agent didn't pick up the credential.
3. Surface exact API `error` strings on 4xx/502 (e.g. "Only organisation admins can connect shared organisation VPS credentials.") — do not retry as a different scope to bypass a 403.

## Source of truth

Route implementations live under `app/api/v1/llm-providers/**`. Provider registry in `lib/llm-providers/providers.ts`; VPS sync in `lib/llm-providers/sync-hermes.ts`; org-write guard in `lib/llm-providers/org-guard.ts`. If this skill and the route disagree, the route wins — update this skill immediately.

## Cross-references

- `system-auth` — token/credential minting doctrine
- `agent-runtime-ops` — Hermes profile links, linked computers, and the VPS targets these connections sync to
- `platform-ops` — API key management surface
