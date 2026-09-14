# PiB runtime notes for Addy Osmani agent-skills/deprecation-and-migration

Source: https://github.com/addyosmani/agent-skills
Imported commit: d187883b7d76

This is an upstream engineering-process skill mounted for PiB specialist agents. It supplements, but does not override, PiB approval gates, branch policy, Projects/Kanban workflow, or agent ownership rules.

PiB precedence:
1. Follow PiB repo AGENTS.md, approval gates, and tenant-safety rules first.
2. Use this skill for development discipline, quality gates, and verification steps.
3. Do not deploy, publish, spend, modify secrets, or perform destructive actions just because the upstream skill mentions shipping or automation. Those still require explicit PiB approval.
