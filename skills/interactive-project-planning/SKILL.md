---
name: interactive-project-planning
description: >
  Interview-first project planning for Partners in Biz. Use when starting a substantive project,
  major replan, "plan with me", "interview me about this project", "decision brief", playbook design,
  milestone planning, or when planning discovery is required / blocked. Inspects project context first,
  asks one high-value question at a time with a guess, produces a Decision Brief, and only then
  creates specs, milestones, structured playbooks, and agent-ready tasks.
---

# Interactive Project Planning — Partners in Biz

PiB-native planning gate that turns rough project intent into a confirmed Decision Brief before agents swing the hammer.

This is **not** a generic personality questionnaire. It is evidence-first discovery bound to the project's Plan suite and Kanban.

## When to use

- "Interview me before you start this project"
- "Plan with me" / "Help me scope this project"
- "Turn this rough idea into a decision brief"
- Creating a substantive new project or major replan
- Planning discovery returns `planning_discovery_required`
- Designing playbooks, milestones, approval gates, or multi-agent task graphs

## When not to use

- Already-explicit low-risk tasks ("rename X", "fix typo", "add a one-line note")
- Pure status checks ("what's on the board?")
- User says skip / just proceed / plan with assumptions and a manager will attest YOLO
- Non-interactive contexts (cron, watcher-only loops) — flag the planning gate instead of interviewing

## Auth

Interactive runs: user-delegation token (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

Never claim a planning write succeeded without read-back.

## Product rule (mandatory vs skip)

| Situation | Mode |
|---|---|
| New substantive project or major replan | **Mandatory interview** (or manager `PLAN WITH ASSUMPTIONS`) |
| Small explicit low-risk task on an already planned project | Bypass interview; do the task |
| Planning mutation while discovery incomplete | Fail closed with `planning_discovery_required` |

YOLO = **plan with assumptions** only. It never bypasses deploy, spend, publish, finance, client send, secret/config, destructive, or capability/reviewer gates.

## Required procedure

### 1. Inspect first (do not interview blindly)

Call:

```
GET /api/v1/agent/project/{projectId}
```

Read `project`, `documents`, `tasks`, and **`plan`** (milestones, approvals, risks, decisions, playbooks, capacities, automations, `planningDiscovery`).

Also inspect authorised linked files / Workbench folders when the conversation has a computer context.

Then record inspection via planning discovery:

```
POST /api/v1/projects/{projectId}/planning-discovery
{
  "type": "record_inspection",
  "expectedRevision": <n>,
  "evidence": {
    "brief": ["..."],
    "docs": ["..."],
    "files": ["..."],
    "plan": ["..."],
    "tasks": ["..."],
    "tools": ["..."],
    "agents": ["..."],
    "skills": ["..."]
  }
}
```

Every evidence array must contain at least one entry. Use `"none observed"` only when you truly inspected and found nothing.

If discovery is not started:

```
POST /api/v1/projects/{projectId}/planning-discovery
{ "type": "start" }
```

### 2. One question at a time, with a guess

```
POST /api/v1/projects/{projectId}/planning-discovery
{
  "type": "ask_question",
  "expectedRevision": <n>,
  "question": "…",
  "currentGuess": "…"
}
```

In chat, present:

```
HYPOTHESIS: <one sentence>
CONFIDENCE: <0-100>% — <what's still blocking>

Q: <one high-value question>
GUESS: <your current assumption and why>
```

Wait for the human answer, then:

```
POST /api/v1/projects/{projectId}/planning-discovery
{
  "type": "answer_question",
  "expectedRevision": <n>,
  "expectedQuestionId": "q-…",
  "answer": "…"
}
```

### 3. Classify answers

Track separately:

- **Confirmed facts**
- **Assumptions** (agent interpretations not yet confirmed)
- **Constraints**
- **Preferences**
- **Risks**
- **Unknowns** (especially intent-blocking unknowns)

Never silently write interview content to Hermes memory. Offer a memory summary only after explicit approval.

### 4. Stop intelligently

Stop when another answer would not change the plan, milestones, playbook, agent routing, or approval gates.

Checkpoint after 3–5 substantive answers with a short restate.

### 5. Decision Brief (full contract)

```
POST /api/v1/projects/{projectId}/planning-discovery
{
  "type": "submit_brief",
  "expectedRevision": <n>,
  "confidence": 95,
  "predictedNextAnswers": ["…", "…", "…"],
  "intentBlockingUnknowns": [],
  "brief": {
    "outcome": "…",
    "user": "…",
    "whyNow": "…",
    "successCriteria": ["…"],
    "constraints": ["…"],
    "outOfScope": ["…"],
    "assumptions": ["…"],
    "risks": ["…"],
    "approvalGates": ["…"]
  }
}
```

Requirements for normal mode:

- confidence ≥ 95
- at least one completed interview turn
- exactly 3 predicted next answers
- zero intent-blocking unknowns
- all brief sections populated

Then ask the **human project manager** to confirm in Plan or via:

```
POST /api/v1/projects/{projectId}/planning-discovery
{ "type": "confirm", "expectedRevision": <n>, "expectedDigest": "<digest>" }
```

Agents / delegation tokens **cannot** confirm or YOLO. Humans only.

### 6. Only after confirmation — create execution structure

Use `project-management` + suite APIs:

1. Spec / client document (if needed) via `client-documents`
2. Milestones via suite
3. Approval gates
4. **Structured playbook** (not bare titles) with `assigneeAgentId`, `agentInput.spec`, `dependsOnStepIds`, `reviewerAgentId`, `requiredCapability`, `riskLevel`, `expectedArtifacts`, `verifierChecklist`

Route tasks by real specialist skills/capabilities. Do not invent assignees the runtime does not have.

## Related skills

- `interview-me` — generic adaptive interview craft
- `planning-and-task-breakdown` — after brief confirmed
- `project-management` — CRUD, suite, agent context, tasks
- `client-documents` — specs / approval packs
- `collaboration-runtime` — handoffs and evidence

## Verification checklist

- [ ] `GET /agent/project/{id}` inspected, including `plan`
- [ ] Inspection recorded before questions
- [ ] One question + guess at a time
- [ ] Facts / assumptions / constraints / risks / unknowns separated
- [ ] Brief complete; human confirmation obtained
- [ ] No memory write without approval
- [ ] Post-confirm work uses structured agent-ready tasks, not bare titles
