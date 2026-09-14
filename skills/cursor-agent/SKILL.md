---
name: cursor-agent
description: Use when a Hermes agent (Mac or VPS) must kick off an autonomous Cursor coding agent via the headless cursor-agent CLI. Covers install paths, auth (Mac OAuth vs CURSOR_API_KEY), the --print -f --output-format json invocation contract, worktree isolation, and parent-verifies-before-reporting.
---

# Cursor Agent Lane (headless `cursor-agent`)

Drive Cursor's autonomous coding agent from a Hermes agent session, on any fleet host. The agent runs Cursor's own CLI in the background on the target repo, then the parent Hermes agent verifies before reporting.

## When to use
- Peet or a specialist wants a bounded implementation/review task executed by a Cursor agent on a repo.
- Local lane (Mac) or cloud lane (VPS) — same contract, different auth.
- Read-only investigation of a repo: use `--mode ask` / `--mode plan` (no edits).

## Install paths
- **Mac (local lane):** already installed at `~/.local/bin/cursor-agent` (versioned self-managing install under `~/.local/share/cursor-agent/versions/<ver>/`), authenticated via the Cursor app's `~/.cursor/cli-config.json` authInfo (OAuth). No key needed.
- **VPS (cloud lane):** official installer `curl https://cursor.com/install -fsS | bash` (installs to `~/.local/bin/agent` + `cursor-agent`). Auth requires `CURSOR_API_KEY` (or `--api-key`). **Provisioned centrally:** each VPS profile's systemd unit loads `EnvironmentFile=/etc/hermes/profiles/<profile>.env`, which now carries `CURSOR_API_KEY` (all 16 profiles, perms 600). If the var is not already in your process env (running agents started before the key landed), source it explicitly first:
  ```bash
  # Running agents started before the key landed won't have it in env yet — source the profile env file:
  set -a; . /etc/hermes/profiles/<PROFILE>.env; set +a   # e.g. <PROFILE>=pip, theo, maya, …
  ```
  (The systemd unit for every profile already loads this file via `EnvironmentFile`, so restarted/started agents get `CURSOR_API_KEY` automatically — sourcing is only a fallback for processes already running.) Bare run errors: `Authentication required… set CURSOR_API_KEY environment variable`.
- Version check: `cursor-agent --version` (VPS 2026.08.25 > Mac 2026.08.11 as of 2026-08-28).

## Invocation contract (proven)
```bash
cd <repo>
cursor-agent --print -f --output-format json "<task>"
```
- `--print` = non-interactive, stdout only (full write + shell tool access).
- `-f` / `--force` = trust the directory + force-allow commands. **Required** for scripted runs — without it the directory-trust gate blocks with a prompt.
- `--output-format json` = parseable result (`--output-format text|json|stream-json`, only valid with `--print`).
- Read-only lanes: `--mode plan` (planning) or `--mode ask` (Q&A) — no repo edits.
- Model selection: `--model <id>` (e.g. `gpt-5`, `sonnet-4-thinking`); list with `cursor-agent --list-models`.
- Resume: `--resume <chatId>` / `--continue`.
- **Do NOT run without a worktree/branch.** Check out an isolated worktree on the task branch before invoking; never point Cursor at a dirty shared checkout.

## Branch / worktree policy
- PiB web repo: stay on `development`, never `main` (see AGENTS.md). Use a dedicated worktree/branch per task so parallel agents don't collide.
- Client repos: work on the repo's normal working branch or an isolated task branch per repo conventions.

## Orchestration pattern (parent-verifies)
1. **Define the contract** in the task: goal, repo path, branch/worktree, files of interest, tests to run, expected artifact.
2. **Constrain side effects:** may the agent edit files, commit, push, open PRs — or report only? State it in the prompt.
3. **Invoke** per the contract above; capture stdout (JSON).
4. **Require verifiable handles:** changed file paths, command output, branch names, commit SHAs.
5. **Parent verifies** — read the diff/files/test output yourself before reporting success. Never trust self-reported success.
6. **Burn/credits note:** Cursor agent runs consume the authenticated account's Cursor credits/quota (same as using the IDE). Cost applies per invocation — flag before long jobs.

## Explicit non-goals
- This skill is **not** the PiB chat-Model provider rail — Cursor is not a chat inference provider (`UNSUPPORTED_CURSOR_NOTE`). BYOK credential management for orgs/users is the separate `cursor-agent-tool-credential-byok` spec (Path B), not this skill.
- This skill does not provision, rotate, or store API keys — auth is pre-provisioned per fleet host (`CURSOR_API_KEY` on VPS env files, OAuth on Mac). Never copy the Mac OAuth token to a server.
- This skill does not decide *what* a Cursor agent builds — the orchestrating agent writes the bounded task contract. No unbounded "fix everything" invocations without scope.

## Pitfalls
- `timeout` is not a macOS default — use the terminal tool's own `timeout` param.
- Bare `--print` without `-f` hangs on the directory-trust gate → always pass `-f`.
- Wrong npm package: `npm install -g cursor-agent` installs an unrelated 3-package tool with **no binary** — use the official installer or the versioned runtime.
- Do not copy the Mac OAuth token (`~/.cursor/cli-config.json` authInfo or the Cursor app LevelDB) to a server — the supported headless auth is `CURSOR_API_KEY`.
- On VPS, PATH: installer puts binaries in `~/.local/bin` — `export PATH="$HOME/.local/bin:$PATH"` if not already set.

## Verification
After any install/auth change: run `cursor-agent --version`, then a smoke test in a scratch dir:
```bash
cd /tmp && cursor-agent --mode ask --print -f "Reply with exactly: CURSOR_LANE_OK"
```
Expect `CURSOR_LANE_OK`, exit 0.

## Related skills
| Skill | Why |
|---|---|
| `pib-platform-code-operations` | PiB platform repo workflows — branch policy, delivery gates |
| `software-delivery-workflows` | Planning/spike/debug/test/review cycles that a Cursor agent may execute |
| `agentic-coding-cli-workflows` | Delegating implementation/review to autonomous coding agents generally |
| `vision-bridge-modlens` | Text-only-model image reading bridge (sibling pattern for cross-fleet tooling) |
