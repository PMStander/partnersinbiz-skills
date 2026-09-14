# Finish Gate — fresh-reviewer pass for design/Studio tasks

Research: ZTTo7g6CU80u1uUSZvoC recommendation P2. Repo tooling:
`lib/design-finish-gate/` + `scripts/design-finish-gate.ts`
(`npm run design:finish-gate -- prepare|verify`). Tests:
`npm run test:design-finish-gate` (41 checks).

## The rule

A web/design/Studio task is NOT done because the builder says so. Before a
done claim, a SEPARATE review pass in a FRESH context (never the builder
thread, never self-grading) grades the delivered surface against the brief
contract and returns a verdict:

- **ship** — every promise in the brief contract is resolved.
- **fix** — some promises partial; the builder iterates, at most 2 fix rounds.
- **rebuild** — a promise is unresolved, or fix rounds are exhausted.

Scoring is promise-by-promise: resolved / partial / unresolved per promise,
from screenshot (or Studio artifact) evidence vs the brief.

## When to run it

Any task that ships a visual surface: pages/sections, dashboards, landing
pages, Studio artifacts, docs with visual output, "polish/redesign/audit"
requests. Run it after the detector passes and before the task is marked done.

## Workflow (agent)

1. Prepare the contract:

   ```bash
   npm run design:finish-gate -- prepare \
     --brief-file /tmp/brief.md --title "Landing redesign" \
     --screenshots /tmp/hero.png,/tmp/mobile.png \
     --builder-agent theo --round 1 --max-fix-rounds 2 --json
   ```

   This prints a JSON envelope: `contract` (schema pib-design-finish-gate/v1)
   with `promises` (extracted from the brief bullets) and the self-contained
   `reviewerPrompt`. Optional `--vision` runs ModLens over the screenshots and
   attaches OCR + layout transcripts so a text-only reviewer can inspect them
   (model/provider resolve from the real ModLens config, or override with
   `--vision-model` / `--vision-provider`).

2. Hand `contract.reviewerPrompt` to a FRESH reviewer context (delegate_task /
   separate run). NEVER answer it in the builder thread — the gate rejects
   reviewerAgentId === builderAgentId as self-grading (exit 1).

3. Verify the reviewer's JSON output:

   ```bash
   npm run design:finish-gate -- verify \
     --contract /tmp/contract.json --reviewer-output /tmp/verdict.json --json
   ```

   Exit codes: 0 ship / 2 fix (rounds remain) / 3 rebuild (or fix-rounds
   exhausted) / 1 failure. The report is promise-by-promise with strengths,
   concerns, fix requests. Evidence fail-closed: a `ship` verdict with NO
   evidence (no screenshots, no vision transcripts, no reviewer evidence
   citation) escalates to exit 1 — missing evidence never reads as resolved.
   Code/tooling reviews supply a real `evidence` citation (files + commands
   inspected), which counts as evidence.

4. Only a `ship` (exit 0) may precede a done claim. On `fix`, do the fixes,
   bump `--round`, re-run with the same fresh-reviewer discipline (max 2 fix
   rounds). On `rebuild`, the task goes back to the builder for a real redo.

## Studio artifacts

`buildStudioReviewContract()` (lib/design-finish-gate/studio.ts) extends the
Studio review tooling: it turns a creative-canvas node into a finish-gate
contract, attaching the T5 `designAudit` stamp (P0-P3 findings) and the
artifact's HTML payload excerpts as evidence for the fresh reviewer.

## Exit code map

| Verdict | Exit | Meaning |
| --- | --- | --- |
| ship | 0 | All promises resolved — task may be marked done |
| fix | 2 | Some partial — iterate (rounds remaining) |
| rebuild | 3 | Unresolved or rounds exhausted — real redo |
| failure | 1 | Malformed input / self-grade rejected |
