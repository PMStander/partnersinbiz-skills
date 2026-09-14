---
name: pib-chat-canvas
description: >
  Emit Partners in Biz chat canvas fences so Messages can render charts, diagrams,
  math, and sandboxed HTML. Use whenever a reply should show a chart, mermaid
  diagram, LaTeX, an HTML artifact, or a generated file instead of a wall of text.
version: 1.0.0
author: Partners in Biz
license: MIT
metadata:
  hermes:
    tags: [partnersinbiz, chat-canvas, chart, mermaid, math, html]
    triggers: ["chart", "graph", "mermaid", "diagram", "latex", "math", "html artifact"]
---

# PiB Chat Canvas

The Messages write-back parses fenced blocks into rich parts. Use these **exact** info strings. Any other info string stays an ordinary code block.

## Fences

### `pib:chart`

JSON body matching ChartPart: `{ kind, x, series, data, title?, unit?, stacked? }`.

- `kind`: `line` | `bar` | `area` | `pie` | `scatter`
- `x`: key in each data row used for the category / independent axis
- `series`: `[{ key, label?, color? }]`
- `data`: array of row objects (`string | number | null` values)

Do not put `type` in the JSON. Malformed JSON is left as a code block — emit valid JSON only, with nothing else inside the fence.

````
```pib:chart
{"kind":"bar","x":"month","series":[{"key":"revenue","label":"Revenue"}],"data":[{"month":"Jan","revenue":12},{"month":"Feb","revenue":18}],"title":"Monthly revenue","unit":"ZAR"}
```
````

### `pib:mermaid`

Raw mermaid source. No JSON wrapper.

````
```pib:mermaid
flowchart LR
  Lead --> Qualified --> Won
```
````

### `pib:math`

Raw LaTeX. No JSON wrapper.

````
```pib:math
E = mc^2
```
````

### `pib:html`

Raw HTML. The platform renders it in a no-script sandboxed iframe (no script, no network, no same-origin).

````
```pib:html
<section><h1>Q3 summary</h1><p>Revenue up 12%.</p></section>
```
````

Never put secrets or raw HTML from a web page into `pib:html`.

### `pib:action`

Emit a structured action card when you finish a tangible outcome (email sent, PR opened, file written, routine run). Body is JSON:

```pib:action
{"kind":"email_sent","title":"Sent invoice follow-up","detail":"To alex@example.com","status":"succeeded","url":"https://mail.example/thread/1"}
```

`kind` one of: `email_sent`, `file_written`, `pr_opened`, `post_scheduled`, `routine_run`, `custom`.

## Limits

From `lib/chat/parts.ts` `PART_LIMITS`. Over-limit parts are dropped.

| Limit | Value |
| --- | --- |
| chart rows | 2000 |
| chart series | 12 |
| mermaid | 20000 chars |
| math | 5000 chars |
| html | 200000 chars |
| file name | 200 chars |
| system event summary | 500 chars |
| action card title | 200 chars |
| action card detail | 2000 chars |

## Table vs chart

Prefer a **markdown table** when the user needs exact values to copy, the set is small (roughly under a dozen rows), or the columns are heterogeneous (mixed units, notes, ids).

Prefer **`pib:chart`** when showing a trend, distribution, part-to-whole, or more than a handful of comparable points. Do not emit both a full table and a chart of the same numbers unless the user asked for both.

## Files

Write files under the working directory and reference them by absolute path; the platform uploads them. Keep file names at or under 200 characters. Do not invent hosted URLs.
