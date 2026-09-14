---
name: studio-artifact-orchestrate
description: >
  Governed Studio artifact planner and specialist router. Use to select the correct PiB Studio
  and named specialist skill, then return a bounded proposal or artifact result with lineage and
  idempotency instead of bypassing domain policy.
---

# Studio Artifact Orchestrate

Gather context with `studio-context-gather` first. This skill coordinates domain work; it does not
duplicate specialist instructions or call providers directly.

## Specialist routing

| Intent | Studio | Reuse |
|---|---|---|
| campaign/social/brand asset | Marketing Studio | `content-engine`; `higgsfield-generate` or `higgsfield-product-photoshoot` only when their provider and rights gates pass |
| edit, captions, render, reframing | Video Editor | existing Video Editor APIs and `platform-ops` |
| manuscript, pages, assembly, publishing packet | Book Studio | existing Book Studio APIs and `platform-ops` |
| strategy, packaging, repurpose, release plan | YouTube Studio | existing YouTube domain skills/APIs and `platform-ops` |
| app workspace, store assets, release readiness | Mobile Apps | `platform-ops` plus existing app-store/mobile specialist skills |

## Workflow

1. Resolve the organisation, Studio, artifact, current version, brand/rights constraints, and
   originating conversation/message. Reject cross-org or unresolved lineage.
2. Choose exactly one primary specialist and list supporting specialists only when necessary.
3. Classify the action: read, bounded draft, generation, review, export, publish, deploy, spend, or
   message. Preview complex/high-risk work; do not mutate it in the planning step.
4. Build `idempotencyKey` from the stable organisation, conversation, origin message, intent,
   target artifact, and source version. Replays must return the existing result or safely no-op.
5. Invoke only an existing permission-checked domain API. Never accept raw secrets, select an
   unapproved model/provider, bypass credits/connections, or invent brand/rights approval.
6. Return human-readable text plus this structured envelope:

```json
{
  "kind": "studio_artifact_proposal",
  "studioKind": "youtube",
  "specialistSkill": "platform-ops",
  "intent": "draft_release_plan",
  "target": { "resourceType": "video", "id": "stable-id", "versionId": "v3" },
  "lineage": { "conversationId": "...", "originMessageId": "...", "sourceArtifactId": "...", "sourceVersionId": "..." },
  "idempotencyKey": "stable-non-secret-key",
  "expectedArtifacts": [],
  "actions": [],
  "blocker": null
}
```

When an authorised domain call creates or updates an artifact, return the same common fields in a
result envelope (do not relabel it as a proposal):

```json
{
  "kind": "studio_artifact_result",
  "studioKind": "youtube",
  "specialistSkill": "platform-ops",
  "intent": "draft_release_plan",
  "target": { "resourceType": "video", "id": "stable-id", "versionId": "v4" },
  "lineage": { "conversationId": "...", "originMessageId": "...", "sourceArtifactId": "...", "sourceVersionId": "v3" },
  "idempotencyKey": "stable-non-secret-key",
  "artifacts": [{ "resourceType": "release_plan", "id": "stable-result-id", "versionId": "v1", "canonicalLink": "/portal/youtube-studio?..." }],
  "actions": [],
  "blocker": null
}
```

When the same idempotency key has already completed, return the stored result without invoking the
specialist or domain mutation again:

```json
{
  "kind": "studio_artifact_existing_result",
  "replayed": true,
  "idempotencyKey": "stable-non-secret-key",
  "result": { "kind": "studio_artifact_result", "target": { "resourceType": "video", "id": "stable-id", "versionId": "v4" }, "artifacts": [] },
  "blocker": null
}
```

Proposal, result, and existing-result envelopes must all preserve `studioKind`, specialist, intent,
target, lineage, idempotency, actions, and blocker information either directly or in the nested
stored result. A replay is evidence of an existing result, never evidence that a new mutation ran.

Rich parts contain stable IDs, never untrusted full records. The server must re-resolve every ID
before rendering data or enabling an action.
