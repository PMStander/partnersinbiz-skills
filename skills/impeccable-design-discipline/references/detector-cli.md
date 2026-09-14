# Impeccable CLI — Detector Reference (verified 2026-08-08, CLI 3.5.0)

## Install/run

```bash
# No-install run (Node 22.12+)
npx -y impeccable --version        # 3.5.0
npx -y impeccable help             # full command list

# Harness skill install (not needed for PiB Layer 1)
npx skills add pbakaus/impeccable
```

## detect usage

```bash
npx -y impeccable detect [file-or-dir-or-url...] [options]

# JSON output (machine-readable; use this in agent evidence)
npx -y impeccable detect src/ --json
npx -y impeccable detect https://example.com --json

# Scope to design domains (comma-separated): type, layout
npx -y impeccable detect src/ --json --scope type,layout

# Mobile-width URL pass
npx -y impeccable detect https://example.com --json --viewport 390x844

# Skip project config / inline ignores / DESIGN.md context / advisories
--no-config --no-inline-ignores --no-design-system --no-advisory

# Text mode: --quiet prints only final finding count
```

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Clean — no failing findings |
| 2 | Findings found — fix before shipping |
| 1 | Scan error (bad path/URL, crash) |

Verified on this runtime: sample slop page -> exit 2 with findings JSON;
clean page -> exit 0 with `[]`.

## JSON finding shape

```json
[
  {
    "antipattern": "low-contrast",
    "name": "Low contrast text",
    "description": "Text does not meet WCAG AA contrast requirements...",
    "severity": "warning",
    "category": "quality",
    "file": "/path/to/file.html",
    "line": 0,
    "snippet": "2.3:1 (need 4.5:1) — text #000000 on #6a0dad"
  }
]
```

`severity`: warning | error. `category`: slop | quality (and more).
Advisory findings are listed separately and never affect exit code.

## Known rule ids (sample)

low-contrast, tiny-text, ai-color-palette, marketing-buzzword, overused-font,
bounce-easing, nested-cards, side-tab-borders, glassmorphism,
kickers/eyebrows, italic-serif-hero, gradient-text, dark-glow, em-dash,
skipped-headings, long-line-length, broken-images, script-errors,
cramped-padding, flat-hierarchy, icon-tile-stacks, design-system-drift ...

Run `npx -y impeccable detect <path> --json` to see the live rule set; the
rule list evolves between CLI versions.

## Ignores & config

Project config: `.impeccable/config.json` and `.impeccable/config.local.json`:
- `detector.ignoreRules` — rule ids to skip
- `detector.ignoreFiles` — file paths to skip
- `detector.ignoreValues` — specific values to skip
- `detector.designSystem.enabled` — DESIGN.md drift rules

Inline comments (travel with the file):
```html
<!-- impeccable-disable overused-font -- exported brand doc -->
<!-- impeccable-disable-line rule-id -->
<!-- impeccable-disable-next-line rule-id -->
```
No rule id or `*` = all rules for that scope.

## Command vocabulary (24 commands, verified via `impeccable help`)

Create: impeccable, shape, craft (deprecated)
Evaluate: critique, audit
Refine: typeset, layout, colorize, animate, delight, bolder, quieter, overdrive
Simplify: distill, clarify, adapt
Harden: polish, optimize, harden, onboard
System: init, document, extract, live

See SKILL.md pillar 1 for the mapping table and PiB usage rules.

## Troubleshooting

- `npx` prompts to install -> use `npx -y`.
- Node < 22.12 -> CLI may fail; check `node --version`.
- URL scans need network access + a reachable URL; static file scans need no network.
- Never fabricate findings; if the scan errors (exit 1), report the blocker.
