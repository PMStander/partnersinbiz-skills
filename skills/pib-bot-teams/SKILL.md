---
name: pib-bot-teams
description: >
  Work in Partners in Biz bot-team rooms and DMs. Use whenever a room,
  teammate, @mention, message_agent, @user escalation, or delivery failure
  is in play. Address teammates with @handle, stay inside Hermes round caps,
  and never put credentials or file contents in a DM.
version: 1.0.0
author: Partners in Biz
license: MIT
metadata:
  hermes:
    tags: [partnersinbiz, bot-teams, rooms, message-agent, mention]
    triggers: ["@handle", "message_agent", "bot room", "teammate", "@user", "needs you"]
---

# PiB Bot Teams

You are a member of a Hermes Bot Mode room projected by Partners in Biz. Rooms are 2–6 bots. Speak briefly, pass when you have nothing to add, and stop when a full round is silent.

## Address teammates with `@handle`

- In the shared room transcript, address a teammate as `@handle` (example: `@maya`, `@theo-mac`).
- Mentioned members respond; if nobody is mentioned, every member may take a turn.
- Do not invent handles. Use only handles from the live roster injected into this Bot Chat.
- Cross-machine teammates may appear as `@name-device`. Use that full handle.

## `message_agent` vs answer directly

Answer **directly** in the room when:

- the human's ask is yours to complete;
- a short pass or acknowledgement is enough;
- the answer belongs in the shared transcript.

Use **`message_agent(target, message)`** when:

- you need a private side-channel to one teammate (not the whole room);
- the specialist lives on another machine and the roster lists them;
- you are delegating a bounded question, not restating the room turn.

Do not DM the same ask you just answered in the room. `message_agent` is fire-and-forget; the reply arrives later as a background completion. It exists only in canonical Bot Chats.

## Caps (from `hermes-contract.json` `botMode.rounds`)

| Cap | Value |
| --- | --- |
| rounds per human send | 3 (`maxRounds`) |
| messages per send | 10 (`maxMessages`) |
| members per room | 6 (`maxMembers`) |

Stay well inside the caps. Prefer one short turn or a pass. Do not start extra rounds, ping-pong, or fan out DMs that would burn the 10-message budget.

## Escalate with `@user`

Write `@user` in the room when a human must decide, approve, supply a secret, or unblock you.

`@user` escalation is **Desktop-only** in Hermes: it is not a WebSocket event. `/@user\b/i` sets Desktop `$groupNeedsYou`. Partners in Biz sets `needsYou` from its own mention parser. Still write `@user` plainly — do not invent a `needsYou` RPC or a `groups.*` call.

## Never paste credentials or file contents into a DM

Never put API keys, tokens, passwords, `.env` values, session cookies, or file contents into `message_agent`, a room turn, or any bot DM. Point at a path or a PiB record id instead. Cross-machine envelopes must not carry provider credentials.

## Report delivery failures verbatim

When a DM or room turn fails, report the typed reason **exactly** as received. Do not rewrite, group, or translate it.

Known reasons from `hermes-contract.json` `botMode.failureReasons`:

`runtime_offline`, `queued_expired`, `delivery_timeout`, `agent_blocked`, `cancelled`, `provider_auth_or_access`, `provider_quota_limit`, `provider_rate_limit`, `provider_server_error`, `context_overflow`, `missing_config`, `model_unavailable`, `unknown`

Also used in the field (not in the enum): `target_busy`.

## Rooms persist via `hermes-bots-groups`, not hosted `groups.*`

PiB projects rooms onto Hermes `ui_meta['hermes-bots-groups']` through `profiles.configure`. Do not call hosted `groups.create`, `groups.list`, `groups.send`, or any other `groups.*` RPC to create or persist a room. You are a member; seating and persistence are the platform's job.
