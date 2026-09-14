# Open Notebook source summary

Repository: https://github.com/lfnovo/open-notebook
Imported commit: d39af0766051
License: MIT
Durable local clone: /var/lib/hermes/open-source-ai-projects/open-notebook

Upstream description: an open source, privacy-focused alternative to Google's NotebookLM. It supports self-hosted/private research workspaces, 18+ model providers, PDFs/videos/audio/web pages, vector and full-text search, chat with sources, and podcast-style outputs.

Key upstream boundaries for PiB:
- It is an application, not a drop-in Hermes SKILL.md package.
- Provider/API keys are configured in the app/runtime and must stay out of chat and committed files.
- Self-hosting improves data control but does not remove PiB approval requirements for client-private ingestion.
