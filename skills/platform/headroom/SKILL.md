---
name: headroom
version: "2026-06-13"
description: Evaluate or roll out Headroom AI token/context compression for PiB agents and apps. Use when Peet asks to save AI costs, compress agent context/tool outputs, add a proxy/MCP compression layer, or measure token savings.
author: Partners in Biz / Pip
license: Apache-2.0 upstream reference
metadata:
  source_repository: https://github.com/chopratejas/headroom
  imported_commit: 9b7b436b0411
  owner_agent: theo
  related_agents: [pip, qa-release, data]
  approval_gates: [access_secret, deploy]
---

# Headroom AI Cost Optimizer

## What this skill is for

Use this when evaluating or integrating Headroom, an open-source local-first context compression layer for AI agents and apps. Upstream positions it as a library, proxy, wrapper, and MCP server that can reduce tokens on logs, tool outputs, RAG chunks, files, and conversation history.

## Ownership

- Theo owns technical evaluation, installation, proxy/MCP integration, and any runtime config changes.
- Vera/data owns before/after cost and quality measurement.
- Quinn/qa-release owns rollout verification when a live agent/profile is affected.
- Pip coordinates approval, affected-agent scope, and evidence capture.

## PiB safety rules

1. Do not enable Headroom on live PiB agent profiles, production APIs, or client workflows without explicit approval for the affected profiles/services.
2. Do not route secrets, credentials, private client documents, or raw mailbox/CRM exports through a new compression/proxy layer until the storage, retention, and retrieval behavior has been reviewed.
3. Do not paste provider keys or proxy credentials into chat or committed files.
4. Measure before changing defaults. Token savings without quality checks are not enough.
5. Keep rollback simple: document exactly how to disable the wrapper/proxy/MCP and restore the previous provider endpoint.

## Evaluation checklist

1. Define the target: agent CLI wrapper, app library, OpenAI-compatible proxy, MCP tool, or offline compression experiment.
2. Use a non-sensitive workload first: logs, public repo search output, or synthetic RAG chunks.
3. Capture baseline token/cost/latency and task correctness.
4. Run Headroom compression and compare output quality plus savings.
5. If rollout is proposed, create a Projects/Kanban implementation task with affected agents, risk level, rollback plan, and QA evidence.
6. Only after approval, let Theo apply profile/runtime changes and Quinn verify.

## Useful upstream commands

```bash
pip install "headroom-ai[all]"
headroom perf
headroom proxy --port 8787
headroom mcp install
```

Run these in an isolated venv or approved service environment. The PiB VPS uses Python 3.12 and PEP 668, so use a venv/uv rather than global pip.

## Verification evidence

A valid Headroom report includes:

- Upstream commit/version used.
- Workload description and sensitivity classification.
- Baseline and compressed token counts/cost estimates.
- Correctness/quality comparison.
- Latency and failure-mode notes.
- Rollback instructions.
- Approval status for any live rollout.
