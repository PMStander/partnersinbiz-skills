# Design Context Template (PRODUCT.md/DESIGN.md equivalent)

Copy this template per client into
`agents/partners/wiki/design-context/<client-slug>/` (product.md, design.md).
Fill it via the discovery interview (`/impeccable init` equivalent) and a live
site / repo scan (`/impeccable document` equivalent). Every web/design/SEO task
for the client MUST read these files before generating.

## product.md — who the product is for and how it speaks

```markdown
# Design Context — <Client Name>

Client: <name> · Domain/slug: <client-slug> · OrgId: <orgId> · Updated: YYYY-MM-DD
Source: <brief/live-site/interview refs>

## Platform & surface inventory
- What the product is and the surfaces it has (marketing site, portal, docs, ...)

## Users
- Who uses it, their jobs-to-be-done, and the primary tasks per surface

## Positioning
- One-line positioning; what makes this client distinct from generic SaaS

## Evidence
- What has been proven to work (test results, client feedback, analytics if any)

## Voice
- Tone words (e.g. warm/expert, blunt/technical, playful/premium)
- Copy do's and don'ts; banned words/phrases

## Anti-references
- Sites/styles the client explicitly does NOT want to look like

## Surface modes
- Tag each surface: Persuade (landing) / Operate (dashboard) / Read (docs) /
  Experience (portfolio) — this changes what the design must accomplish
```

## design.md — the visual system (Google Stitch spec shape)

```markdown
# Design System — <Client Name>

## Colors
- Palette: primary/secondary/neutral/semantic (hex)
- Usage rules; gradients (avoid AI-tell purple/violet unless on-brand)

## Typography
- Type stack (avoid overused: Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, Space Grotesk)
- Scale, weights, hierarchy, line lengths (body ~45-75ch)

## Components
- Buttons, cards, inputs, nav, tables, modals — shapes and rules

## Radii & elevation
- Radius scale; shadow/elevation rules (avoid nested-card slop)

## Motion
- Durations/easing; purposeful animation only (avoid bounce ease tells)

## Rules / do-nots
- Detector-driven constraints (contrast >= WCAG AA, min body 14px, no kickers/eyebrows, ...)
```

## surfaces.md (optional — per-surface briefs)

```markdown
# Surface Briefs — <Client Name>

## /pricing (Persuade)
- Job: convert. Proof points, one primary CTA, no clutter.
## /dashboard (Operate)
- Job: dense, native expectations, task-focused.
...
```

When a local DESIGN.md is written into the site repo itself
(`.impeccable/design.json` / DESIGN.md), the detector's design-system-drift
rules unlock — do that whenever the repo is available (Layer 2+).
