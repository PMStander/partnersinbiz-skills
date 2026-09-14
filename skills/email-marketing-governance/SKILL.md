---
name: email-marketing-governance
description: >
  Safely inspect, draft, review, approve, schedule, activate, enroll, replay, and
  analyze Partners in Biz email marketing. Trigger for email campaigns,
  broadcasts, journeys, audiences, sender policies, replies, lead capture,
  consent, deliverability, or provider-event reconciliation.
---

# Email Marketing Governance

Use the platform's canonical email APIs and preserve tenant, consent, approval,
and replay boundaries. This skill complements `email-outreach`; it defines the
operating rules for actions that can create client-visible sends.

## Non-negotiable rules

1. Resolve and retain one organisation scope. Never copy resource IDs between
   organisations or infer ownership from caller-supplied webhook/capture data.
2. Treat marketing consent as opt-in. Missing or ambiguous consent, suppression,
   preference, sender, approval, or provider ownership evidence fails closed.
3. Drafting, preflight, analysis, and approval requests are allowed only within
   the caller's capability policy. Sending, scheduling, activating, enrolling,
   replaying, or resuming requires server-verified approval for the exact
   immutable resource/version being executed.
4. A maker cannot approve their own client-visible work. Never fabricate,
   summarize into, or reuse an approval ID for changed content or audiences.
5. Use configured sender policies. Never substitute an unverified From address
   or expose provider credentials, webhook secrets, API keys, or raw recipient
   data in output.
6. Prefer dry-run/preflight and audience estimates before requesting approval.
   Report blocked recipients and reasons without bypassing them.
7. Preserve idempotency keys for retries. Replay only failed/dead-letter work,
   keep the original organisation and immutable workflow version, and report the
   replay result. Do not turn a retry into a duplicate send.
8. Provider webhooks and capture attribution are evidence, not authority. Trust
   only server-resolved tenant ownership and signed/configured lineage.

## Safe operating sequence

1. Read the scoped program, audience version, sender policy, consent/preference
   state, and current approval state.
2. Draft or edit, then run preflight. Show material changes, estimated audience,
   exclusions, sender/reply routing, schedule/timezone, and required approval.
3. Request human approval for the exact immutable snapshot. Stop if it is absent,
   stale, self-approved, rejected, or linked to another organisation/resource.
4. Invoke the governed schedule/activation/enrollment/send endpoint once with a
   stable idempotency key. Never call a provider directly.
5. Read back persisted status and audit evidence. Report queued/sent/skipped/
   failed counts honestly; do not equate provider acceptance with delivery.

## Reply, capture, and analytics boundaries

- Replies remain organisation-scoped, retain SLA/assignee state, and require an
  idempotency key for corrections. Out-of-order retries return current state.
- Progressive capture continues against its pinned immutable schema. Hidden
  lineage is server-derived; caller-provided hidden or unknown fields are invalid.
- Opens affected by privacy proxies are labelled, not presented as human reads.
  Use immutable provider events and reconciliation results for rollups.

## Stop conditions

Stop and return the exact blocker when legal approval, provider/domain readiness,
VPS skill parity, a test recipient, production promotion, or external-send
authority is missing. Never perform a production deploy, provider test send, or
client-visible send merely because code and tests are green.

