---
name: pib-routines
description: >
  Create, list, run, and manage PiB-owned bot routines (schedule + event
  triggers). Use when the user asks about recurring bot work, cron-like
  routines, /routine, GitHub/Slack/Linear event triggers, or bot desk routines.
version: 1.0.0
author: Partners in Biz
license: MIT
metadata:
  hermes:
    tags: [partnersinbiz, routines, cron, webhooks, bot-desk]
    triggers: ["/routine", "bot routine", "schedule routine", "event trigger"]
---

# PiB Routines

Partners in Biz owns routine triggers and the run ledger. Execution posts into a
per-routine mirror conversation (simplified path — not Hermes sidecar cron).

Feature flag: `botRoutinesEnabled` (default off).

## Collections

- `bot_routines` — routine definitions
- `bot_routine_runs` — run ledger
- `bot_routine_event_dedupe` — event idempotency (`${routineId}_${eventId}`)
- `org_integrations` — GitHub / Slack / Linear signing secrets

## API

### List / create

`GET /api/v1/bots/:botId/routines?orgId=…`  
Merges Hermes cron (`source: cron`), standing goals (`goal`), and PiB routines (`routine`).

`POST /api/v1/bots/:botId/routines` body:

```json
{
  "orgId": "org_…",
  "name": "Morning brief",
  "prompt": "Summarise overnight CRM activity",
  "accessScope": "personal",
  "trigger": { "kind": "schedule", "cron": "0 9 * * *", "tz": "UTC" }
}
```

Event trigger example:

```json
{
  "trigger": {
    "kind": "event",
    "source": "github",
    "filter": { "event": "push" }
  }
}
```

Webhook event routines (`source: webhook`) return a one-time `hookSecret` and `hookId`.

### Manage

- `PATCH /api/v1/bots/:botId/routines/:routineId`
- `DELETE /api/v1/bots/:botId/routines/:routineId` (archives)
- `POST /api/v1/bots/:botId/routines/:routineId/run` — manual fire
- `GET /api/v1/bots/:botId/routines/:routineId/runs` — history

### Auth

- Personal routines: owner only (manage)
- Organisation routines: org admin (`canManageOrgAs`)

### Chat

`/routine name | cron | prompt` returns a `routine_proposal` rich part and a
`create_routine` UI action that POSTs to the routines API (`bodyMode: payload`).

### Cron

`GET /api/cron/bot-routines` with `Authorization: Bearer $CRON_SECRET` every minute.
Claims due schedule routines transactionally, then fires runs.

### Event ingress

- PiB outbound webhooks → `fanoutRoutineEvent(orgId, { source: 'pib', … })`
- `POST /api/v1/routines/hooks/:hookId` — HMAC via `X-PIB-Signature` + `X-PIB-Timestamp`
- `POST /api/v1/integrations/github/webhook?orgId=…`
- `POST /api/v1/integrations/slack/events?orgId=…`
- `POST /api/v1/integrations/linear/webhook?orgId=…`

Settings UI: `/portal/settings/integrations`.

## Dispatch note

`fireRoutine` writes the prompt as a user message into the mirror conversation
and marks the run succeeded when enqueued. Full `enqueueLinkedRun` wiring is
deferred (messages-route coupling).
