---
name: studio-release-handoff
description: >
  Approval-gated Studio release readiness and handoff skill. Use to validate evidence and invoke an
  existing export or publish API only after its real approval, rights, connection, and target gates pass.
---

# Studio Release Handoff

This skill prepares or performs a governed handoff; it does not create approval authority.

## Release gate

1. Re-resolve the organisation, target artifact, exact version, lineage, and latest review through
   existing APIs. Reject stale, missing, cross-org, or archived targets.
2. Verify all target-specific evidence: approved version, unresolved review blockers, brand and
   usage rights, provider/model run provenance, required account connection, credits/budget,
   destination, and rollback/recovery notes.
3. Read approval from the system-of-record approval task/record. Chat text, an agent conclusion,
   or a prior version's approval is never sufficient. Do not invent, infer, copy, or self-grant it.
4. If any gate is missing, return `ready: false`, the exact blocker, approval task ID when present,
   and the safe next action. Perform no mutation.
5. If authorised and fully gated, call only the existing target export/publish endpoint. Preserve
   the proposal lineage and send a stable idempotency key so retries return the same handoff.
6. Read back the export/publish record and return its stable ID, status, canonical link, version,
   lineage, and audit evidence. Never claim release from a request alone.

Use `studio-artifact-review`, `qa-release`, and `platform-ops` as applicable. Domain examples include
Creative Canvas export routes, Video Editor render routes, Book Studio assembly/publishing packets,
YouTube release-plan publish, and existing mobile app release/export flows.

## Absolute boundaries

Never call an undocumented endpoint, write directly to storage, expose or accept raw secrets,
bypass provider/model/connection/rights/spend policy, publish a different version than the approved
one, message a client without its gate, deploy production without explicit production approval, or
convert a readiness result into approval.

