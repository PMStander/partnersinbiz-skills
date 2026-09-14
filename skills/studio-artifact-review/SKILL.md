---
name: studio-artifact-review
description: >
  Evidence-led Studio artifact reviewer. Use to compare versions and expected outputs, produce an
  attention card, and record a change request or approval only through an authorised existing API.
---

# Studio Artifact Review

## Procedure

1. Use `studio-context-gather` to resolve the current artifact and source version in the same org.
2. Load the proposal's expected artifacts, prior version, current version, review checklist, rights
   evidence, provider/run evidence, and existing approval state through current read APIs.
3. Compare evidence and versions explicitly. Separate verified facts, regressions, unknowns, and
   policy blockers. Never interpret an agent assertion as approval evidence.
4. Default to a read-only review. Record a change request or approval only when the caller is
   authorised and the domain already exposes that exact review API. Otherwise return the proposed
   action and required approval gate without mutation.
5. Use the proposal lineage and idempotency key plus review decision/version. A replay must not
   duplicate comments, decisions, approvals, tasks, or messages.

## Output

Return human-readable findings and a `studio_artifact_review` envelope containing stable artifact
and version IDs, evidence checked, pass/fail/unknown checks, requested changes, recorded action (or
`null`), lineage, idempotency key, permission-checked actions, and an explicit blocker/approval
object. Emit an attention card for unresolved material findings.

## Boundaries

Do not generate or modify creative output, call providers, access raw secrets, approve on behalf of
a human, export, publish, deploy, spend, or message a client. Do not write directly to storage when
an authorised review API is absent.

