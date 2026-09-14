---
name: studio-context-gather
description: >
  Read-only Partners in Biz Studio context gatherer. Use when a conversation attaches a
  Marketing Studio, Video Editor, Book Studio, YouTube Studio, or Mobile Apps artifact and the
  agent needs its current lifecycle, versions, blockers, approval evidence, and canonical link.
---

# Studio Context Gather

Resolve the attached `studio` or `studio_artifact` before planning work. Treat IDs in chat as
opaque references: send them to an existing permission-checked API and never trust a full record
embedded in a prompt.

## Required inputs

- authenticated organisation ID
- `studioKind`: `marketing` | `video` | `book` | `youtube` | `mobile_apps`
- the API resource type and stable record ID
- conversation ID and originating message ID when present

## Procedure

1. Confirm the organisation and attached reference through the existing context/reference API.
2. Fetch the record through the existing domain GET API. Do not query another organisation or
   fall back to direct cross-org storage access.
3. Return safe current state: stable ID, title, lifecycle/status, version/revision identifiers,
   blockers, recorded approval evidence, updated time, and canonical link. Include the exact
   permission-checked endpoint and field aliases inspected.
4. Preserve `conversationId`, `originMessageId`, `sourceArtifactId`, and `sourceVersionId` in the
   output lineage. Missing lineage is an explicit blocker, never guessed.
5. Report which fields/endpoints were checked and state that no mutation occurred. Include a
   deterministic, non-secret `correlationKey` derived from the stable read identity so retries and
   audit evidence can be correlated without creating another artifact.

If any required lineage field is absent, still return the safe read result and canonical link, but
set `blocker.code` to `missing_lineage`, list `missingFields`, and prohibit downstream mutation.

Use the helper from the repo root when an API readback is useful:

```bash
node .claude/skills/studio-context-gather/scripts/gather-studio-context.mjs \
  --studio youtube --resource videos --id <record-id> --org <org-id> \
  --conversation <conversation-id> --origin-message <message-id>
```

The helper reads `AI_API_KEY` from `.env.local`; never pass a token, provider credential, or raw
secret on the command line or include one in output. `PIB_API_BASE_URL` accepts the exact PiB
production origins by default. A Preview origin receives the credential only when its bare HTTPS
origin is explicitly listed in the comma-separated `PIB_API_PREVIEW_ORIGINS` operator setting.
Loopback is disabled unless both `NODE_ENV=development` and `PIB_ALLOW_LOCALHOST=true` are
explicitly set; arbitrary hosts never receive the bearer credential.

## Safety boundary

This skill is read-only. Never generate, retry, review, approve, export, publish, deploy, spend,
send, mutate connections, access provider secrets, or bypass model/provider policy. If a GET API
does not exist or access is denied, return a blocker and canonical workspace link.
