---
name: conversations-runtime
description: >
  Partners in Biz conversations/chat runtime for Hermes engineers: conversation CRUD,
  message dispatch lifecycle (send/continue/stop/finalize), attachments, model selection,
  context assembly, and agent-message ingestion. Owner: theo. Use when debugging or
  building against /api/v1/conversations/* — not for drafting user-facing chat copy
  (see chat-surface-gather).
---

# Conversations Runtime — Partners in Biz Platform API

## Owner & scope

- Owner: `theo`
- Allowed: `theo`, `qa-release`, `pip` (orchestrator debugging)
- Base path: `https://partnersinbiz.online/api/v1/conversations`
- Related: `system-auth`, `chat-surface-gather`, `collaboration-runtime`

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Route map (shipped)

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/conversations` | List / create conversations |
| GET/PATCH | `/conversations/[convId]` | Read / update conversation metadata |
| GET/POST | `/conversations/[convId]/messages` | List messages / human send (dispatches Hermes or linked-computer run) |
| POST | `/conversations/[convId]/continue` | Continue a pending agent turn |
| POST | `/conversations/[convId]/messages/[msgId]/stop` | Stop an in-flight run |
| POST | `/conversations/[convId]/messages/[msgId]/finalize` | Finalize / mark complete |
| GET/POST | `/conversations/[convId]/agent-messages` | Agent append completed assistant messages (no re-dispatch) |
| GET/POST | `/conversations/[convId]/attachments` | List / upload attachments |
| GET/DELETE | `/conversations/[convId]/attachments/[attachmentId]` | Fetch / remove attachment |
| GET | `/conversations/[convId]/context` | Assembled context for the conversation |
| GET/POST | `/conversations/[convId]/models` | List / select model overrides |

## Agent patterns

### Human message → agent dispatch
1. `POST /conversations/[convId]/messages` with `{ content, ... }` as the human user session.
2. Platform mints a **fresh** short-lived `pib_dlg_*` token on every human-triggered turn and injects it into the Hermes prompt. Do not reuse a stale token from conversation history. Mailbox 401/403 with delegation-evidence is reminted once in-run; never ask the human to remint via chat.
3. Read back assistant message status via `GET .../messages` — do not invent run outcomes.

### Agent append without re-dispatch
Use `POST .../agent-messages` only when the agent already finished work and needs to land rich parts into the thread. Never use it to fake a Hermes run.

### Stop / finalize
If a run is stuck pending, prefer `stop` then report the exact gateway/workspace failure code from the message record.

## Success gate

After any create/update that clients will see:
1. `GET` the conversation or message list
2. Assert the expected message id / status / rich parts exist
3. Surface exact API `error` strings on 4xx — do not retry with a god-key

## Source of truth

Route implementations live under `app/api/v1/conversations/**`. If this skill and the route disagree, the route wins — update this skill immediately.
