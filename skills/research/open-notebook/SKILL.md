---
name: open-notebook
version: "2026-06-13"
description: Operate or evaluate Open Notebook, the local/private NotebookLM-style research workspace. Use when Peet asks for local NotebookLM, self-hosted research notebooks, source ingestion, podcast/audio overview alternatives, or private multi-model research synthesis.
author: Partners in Biz / Pip
license: MIT upstream reference
metadata:
  source_repository: https://github.com/lfnovo/open-notebook
  imported_commit: d39af0766051
  owner_agent: sage
  related_agents: [pip, theo, docs, maya, seo]
  approval_gates: [access_secret, deploy, message_client]
---

# Open Notebook Research Studio

## What this skill is for

Use this when operating or evaluating Open Notebook as a self-hosted, privacy-focused NotebookLM alternative for PiB research workflows.

Open Notebook supports PDFs, videos, audio, web pages, multi-model chat, vector/full-text search, and podcast-style output. The upstream project is an application, not a native Hermes skill, so this wrapper tells agents how to use it safely inside PiB.

## Ownership

- Sage owns research workspace design, source selection, synthesis quality, and evidence-backed recommendations.
- Iris/docs owns client-facing report polish and document packaging.
- Maya uses it for content research packs and repurposing only after sources are approved.
- Silas/seo uses it for SEO research corpora and content evidence.
- Theo owns installation, Docker/runtime debugging, model-provider setup, and any production-like deployment.
- Pip coordinates scope, approvals, task linkage, and cross-agent handoff.

## PiB safety rules

1. Resolve client workspace and orgId before using client material.
2. Do not ingest client-private docs, mailbox exports, CRM/contact exports, credentials, invoices, payroll, banking, legal, or restricted data without explicit scope and approval.
3. Do not paste API keys into chat, wiki, documents, or source files. Provider keys belong in approved profile/runtime secret stores only.
4. Treat Open Notebook outputs as secondary synthesis. Canonical PiB memory remains cowork wiki, Research records/source records, Client Documents, and Projects/Kanban.
5. No Drive sharing, publishing, client-visible delivery, or production deployment without the relevant approval gate.

## Setup/evaluation checklist

1. Confirm the goal: local evaluation, persistent internal service, client-specific research notebook, or migration from Google NotebookLM.
2. Read the upstream README/reference in this skill before changing runtime.
3. If only evaluating, use a throwaway local folder and non-sensitive public sources first.
4. If client data is involved, create or link the Projects/Kanban approval task before ingestion.
5. For installation, hand off to Theo or operate under Theo’s engineering rules.
6. After setup, record: source scope, model/provider configuration category (not secrets), storage location, retention decision, and verification evidence.

## Useful upstream commands

The upstream quick start uses Docker Compose:

```bash
docker compose up -d
```

Default UI/API ports in upstream docs are 8502 and 5055. Do not bind a public interface or long-running service on the VPS without Theo/release approval.

## Verification evidence

A valid setup/evaluation report includes:

- Upstream commit/version used.
- Whether this was public-source-only or client-scoped.
- Runtime mode: local throwaway, internal persistent, or deployment proposal.
- Health check or UI/API reachability evidence.
- A sample non-sensitive source query and output quality notes.
- Open blockers and required approvals.
