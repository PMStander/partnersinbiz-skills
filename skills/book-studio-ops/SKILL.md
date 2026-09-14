---
name: book-studio-ops
description: >
  Book Studio production engine on Partners in Biz: book projects, chapters/pages content
  model, puzzle-page generation, print/ebook assembly (interior PDF, cover PDF, EPUB), the
  generic PATCH-any-resource pattern, format/trim registries, series grouping, rights
  ledgers, decision logs, publishing packets, and the Creative Canvas production bridge
  (open-in-canvas, sync-back, export auto-create). Owner: maya. Use this skill whenever the
  user mentions book studio projects, chapters, manuscript assembly, puzzle books, book
  formats/trims, or publishing packets.
---

# Book Studio Ops — Partners in Biz Platform API

Book Studio's content model (chapters/pages), puzzle generation, print/ebook assembly, and its Creative Canvas bridge — the production surface that turns a book project into real interior PDFs, cover PDFs, and EPUBs. All routes below: auth `admin`, `orgId` via `?orgId=` query (falls back to `x-org-id` header / caller's org).

## Owner & scope

- Owner: `maya`
- Scope: End-to-end book production: projects, briefs, chapters, pages (including puzzle-page generation), series grouping, rights ledgers, decision logs, analytics imports, artifact links, manuscript assembly, and publishing packet generation.
- Base path: `https://partnersinbiz.online/api/v1/book-studio`

## Related skills

- `creative-canvas-ops` — open-in-canvas manuscript/illustration editing, sync-back, exports
- `client-documents` — manuscript export target
- `content-engine`

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Chapters and pages (content units)

Chapters and pages are project-scoped content-unit documents, siblings of the other Book Studio resources (briefs, series, publishing-packets, etc.) served through the same generic resource routes.

### `GET /book-studio/chapters?orgId=...` / `GET /book-studio/pages?orgId=...`
Lists live (non-deleted) records for the org.

### `POST /book-studio/chapters?orgId=...`
Body fields: `projectId`, `title`, `body` (max 900,000 chars — over the limit 400s), `status` (`draft` | `generated` | `edited` | `approved`, default `draft`), `order` (non-negative int), `canvasRunId`.
- `wordCount` is **server-computed** from `body` on every write — a client-supplied `wordCount` is always ignored/overwritten.
- Chapters/pages suppress the generic `stage`/`channel` pipeline fields entirely (they don't apply to content units).

### `POST /book-studio/pages?orgId=...`
Body fields: `projectId`, `title`, `kind` (`illustration` | `colouring` | `comic` | `puzzle` | `activity` | `text` | `front_matter` | `back_matter`), `status` (same content-status enum as chapters), `order`, `imageUrl`, `imageStoragePath`, `caption`, `prompt`, `canvasRunId`, and:
```json
{ "puzzle": { "kind": "sudoku", "seed": 123456, "difficulty": "medium",
    "params": { "words": ["OCEAN", "REEF"] } } }
```
`puzzle` is a composite object: `kind` (required for the object to be kept), `seed` (int), `difficulty` (string), `params` (whitelisted to `words: string[]` or `entries: {word,clue}[]` shape — any other key is dropped), `solutionRef`.

## Generic PATCH for any Book Studio resource

### `PATCH /book-studio/{resource}/{id}?orgId=...`
One endpoint patches every Book Studio resource (`projects`, `briefs`, `series`, `chapters`, `pages`, `artifact-links`, `publishing-packets`, `rights-ledgers`, `package-manifests`, `analytics-imports`, `decision-logs`) — `{resource}` is the same plural-kebab key used in the collection's own GET/POST path.
- Only fields present in the request body are touched — no create-time defaults leak in, and `orgId`/`projectId` can never be changed through a patch (silently stripped even if sent).
- Soft-delete: `{ "deleted": true }` — the record disappears from GET list results but is not physically removed.
- **Invalid enum values 400 instead of silently falling back.** In create mode an out-of-range enum silently falls back to a default; in PATCH mode a *present-but-invalid* value throws, e.g. `PATCH pages/{id}` with `{"kind": "not_a_kind"}` → 400 `invalid value for kind`. This applies to every enum-ish field (`status`, `kind`, gate `status`, rights `status`, package-manifest `qaStatus`, etc.).
- Composite objects (`puzzle`, `packageManifest`, `gates`, `rightsLedger`, `metadata`, `approvalState`, `analyticsSnapshot`, `trim`) **replace wholesale** — Firestore `update()` overwrites the whole top-level key, so patching `puzzle` with a new object never merges with the old one; send the full object you want.
- Cross-org or already-deleted records 404 indistinguishably from records that never existed.

```bash
curl -X PATCH "https://partnersinbiz.online/api/v1/book-studio/pages/page_123?orgId=org_abc" \
  -H "Authorization: Bearer $AI_API_KEY" -H "Content-Type: application/json" \
  -d '{"status": "edited", "imageUrl": "https://.../page-1.png"}'
```

## Project and series content-model fields

Beyond the shared Book Studio fields (title, status, stage, bridgeLinks, gates, etc.), `projects` and `series` accept:

**Projects** — `format` (registry id, validated against the format registry; unknown id → 400 `unknown book format`), `trim` (`{ presetId }`, must resolve to a known preset or 400 `unknown trim preset`), `stylePrompt`, `coverImageUrl`, `creativeCanvasId`, `seriesVolumeNumber` (positive int).

Format registry ids (`BookFormatId`): `story`, `nonfiction`, `kids_picture`, `colouring`, `comic`, `activity_workbook`, `puzzle_sudoku`, `puzzle_word_search`, `puzzle_maze`, `puzzle_crossword`, `puzzle_mixed`. Each format fixes a `layout` (`reflowable` for chapter-based books, `fixed` for page/image-based ones), `contentUnits` (`chapters` vs `pages`), a default + supported trim list, which assembly outputs it produces, and (for puzzle formats) a `puzzleKind`.

Trim presets (`TrimPresetId`): `5x8`, `6x9`, `7x10`, `8x10`, `8.5x8.5`, `8.5x11` — all KDP-spec (0.125" bleed, 300 DPI); `resolveTrimSpec` also derives margins/gutter and paperback spine width from page count.

**Series** — `volumeOrder` (string array of project ids), `sharedMetadata` (`{ authorName, imprint, keywords, categories }`), `sharedStylePrompt`.

## `POST /book-studio/projects/{id}/pages/generate-puzzles?orgId=...`

Generates a batch of deterministic, seeded puzzle pages and creates them as `pages` records in one call.

Body:
```json
{ "kind": "word_search", "count": 20, "difficulty": "medium",
  "params": { "words": ["OCEAN", "REEF", "CORAL"] },
  "startOrder": 40 }
```
- `kind`: `sudoku` | `word_search` | `maze` | `crossword` — must match the project format's `puzzleKind` (or the format must be `puzzle_mixed`), else 400.
- `count`: integer 1–100.
- `difficulty`: `easy` | `medium` | `hard` | `expert`.
- `params`: `{ words: string[] }` for word_search, `{ entries: {word, clue}[] }` for crossword (unknown/other keys dropped).
- `startOrder` (optional): int ≥ 0; defaults to `max(existing live page order for this project) + 1`.
- **Validate-all-before-write**: every one of `count` puzzles is generated and validated first; if any single one fails, the whole call 400s and nothing is written — never a partial batch.
- Seeds are derived from a random base + index, so pages are deterministically reproducible per seed but not predictable batch-to-batch.
- Response: 201 `{ "pages": [ {...created page records...} ] }`, each pre-tagged `kind: "puzzle"`, `status: "generated"`.

## `POST /book-studio/projects/{id}/assemble?orgId=...`

Produces the real, downloadable production files for a book project — this is the actual print/ebook build step, not a preview.

- Loads the project's live chapters/pages, builds whichever of interior PDF / full-wrap cover PDF / EPUB the format calls for (`format.assembly`), and uploads each to Firebase Storage.
- **Readiness gates before building anything**: reflowable formats need at least one chapter with non-empty body (else 422 `AssemblyNotReadyError` "no chapters"); fixed-layout formats need every image-kind page (`illustration`, `colouring`, `comic`, `activity`) to have an `imageUrl`, else **422 `{ "missing": [<page orders>] }`**.
- Writes `packageManifest` back onto the project: `{ status: "generated", version: <incremented from previous>, qaStatus: "pending_review", generatedAt, checksum, files: [{ role, label, href, storagePath, checksum, bytes, pageCount? }] }`. Each file carries its own **sha256 checksum**; the manifest's top-level `checksum` mirrors the interior PDF's (or the first file's, for formats with no interior).
- Also writes a `decision-logs` entry (`decision: "package_assembled"`) summarizing which files were produced.
- **Store upload remains manual per governance** — assembly produces the files and manifest only; nothing here submits to KDP/Google Play Books/Apple Books/etc. (the publishing-packet `manual_upload_review` stage still owns that human step).
- Errors: 404 `book project not found`, 400 unknown format/trim, 422 not-ready / missing assets (as above).

```bash
curl -X POST "https://partnersinbiz.online/api/v1/book-studio/projects/proj_123/assemble?orgId=org_abc" \
  -H "Authorization: Bearer $AI_API_KEY"
```

## Creative Canvas bridge

### `POST /book-studio/projects/{id}/open-in-canvas?orgId=...`

Opens (or creates) a Creative Canvas production board for a book project — same idempotent pattern as the YouTube Studio bridge (see `youtube-studio-ops`).

Response: `{ "canvasId": "canvas_abc", "created": true|false }` — `created: false` and the existing canvas short-circuit if the project is already linked to a live canvas; a stale link (canvas deleted) falls through and re-creates.

What gets seeded, keyed off the project's `format.canvasRecipe`:
- A brief node (title/format/audience/style summary) that every generator references.
- A cover image generation node — always seeded, tagged `data.bookRole: "cover"`.
- `picture_book` / `colouring_book` / `comic_book` recipes → one image generation node per page still missing `imageUrl`, tagged `data.bookRole: "page_illustration"` + `data.bookPageId`.
- `text_book` recipe → one copy-generation node per chapter still needing prose (`status` unset/`draft`/`generated`), tagged `data.bookRole: "chapter_text"` + `data.bookChapterId`.
- `none` recipe (puzzle/activity formats) → brief + cover only; puzzle interiors are always generated deterministically via `generate-puzzles`, never via canvas models.
- Every generation node carries `edit.outputKind: "book_artifact"` so downstream export/routing can identify book outputs in the run stream. Hard cap of 24 generation nodes (cover included) per seed.
- Two-way link stored on both records: `project.creativeCanvasId` ↔ `canvas.linked.bookStudioProjectId`.

### Sync-back (automatic, no endpoint to call)

Completed runs on a linked canvas write back to the book project automatically, scoped to exactly three fields — nothing else in Book Studio is ever touched by canvas sync-back:
- `bookRole: "cover"` run completes → project `coverImageUrl` set to the run's output URL, plus an `artifact-links` record (`canvas-run-{runId}`, idempotent).
- `bookRole: "page_illustration"` run completes → the tagged page's `imageUrl` set, `canvasRunId` stamped, `status` set to `generated`.
- `bookRole: "chapter_text"` run completes → the tagged chapter's `body` set (and `wordCount` recomputed), `canvasRunId` stamped, `status` set to `generated`.
- **Edited/approved content is never clobbered**: a page already `edited` or `approved`, or a chapter whose status isn't `draft`/`generated`, is left untouched even if its generating node completes again.

### Canvas exports/drafts → Book Studio

Exporting a canvas node with `target: "book_studio"` (output kind `book_artifact`) auto-creates a linked book project if the canvas isn't already linked to one — same auto-create convention as `youtube_studio`/`client_document` targets.

```bash
curl -X POST "https://partnersinbiz.online/api/v1/creative-canvas/canvas_abc/exports/draft?orgId=org_abc" \
  -H "Authorization: Bearer $AI_API_KEY" -H "Content-Type: application/json" \
  -d '{ "nodeId": "node_chapter_1", "target": "book_studio",
        "format": "story", "seriesId": "series_abc", "title": "Book title" }'
```
- `format` is **required** on first (unlinked) export — must be a valid format-registry id, else 400 listing the valid ids.
- `seriesId` (optional) must resolve to a live, same-org `book_studio_series` doc, else 400.
- `title` optional — falls back to the canvas's own title.
- Idempotent: if the canvas is already linked to a live, same-org book project, that project is reused (`created: false`) instead of creating a duplicate; response includes `projectId` and `created`.

## API routes to document next

- `GET/POST /book-studio/projects`
- `POST /book-studio/projects/[id]/transition`
- `GET/POST /book-studio/briefs`
- `GET/POST /book-studio/series`
- `GET/POST /book-studio/rights-ledgers`
- `GET/POST /book-studio/decision-logs`
- `GET/POST /book-studio/analytics-imports`
- `GET/POST /book-studio/artifact-links`
- `GET/POST /book-studio/publishing-packets`
- `GET/POST /book-studio/package-manifests`

## Next steps to un-stub this skill further

- Document request/response shapes and the auth level (`viewer`/`member`/`admin`/`system`/delegation-only) per remaining route above.
- Add an `## Agent patterns` / workflow-guide section once at least one end-to-end flow (brief → chapters/pages → assemble → publishing-packet) has been run and verified (write → read-back → report).
- Register any newly-confirmed write-then-verify contract in the pack `verificationContract`.

## Cross-references

- creative-canvas-ops (open-in-canvas manuscript editing)
- client-documents (manuscript export target)
- content-engine
