---
name: video-editor-ops
description: >
  Partners in Biz Video Editor: editor projects/timelines, credit-metered render jobs,
  transcription + translation, TTS voiceover, 9:16 reframe, beat-marker analysis, stock
  footage search/import, LUTs, reusable templates, and the media-preview/proxy-ledger
  cache. Owner: maya. Use this skill whenever the user mentions video editor projects,
  render jobs, transcripts/captions, TTS voices, LUTs, or video templates on the platform.
---

# Video Editor Ops — Partners in Biz Platform API

## Owner & scope

- Owner: `maya`
- Allowed: `maya`, `theo` (runtime/dispatch debugging), `qa-release`
- Risk: medium (credit-metered generation; no publish/spend approval gate of its own)
- Base path: `https://partnersinbiz.online/api/v1/video-editor`
- Related: `system-auth`, `content-engine`, `youtube-studio-ops`, `creative-canvas-ops`

All routes use `withAuth('client', ...)` — any authenticated org member or agent acting for that org, scoped by `orgId` (query param, body field, or the caller's own org). None of these routes require `admin`.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Route map (shipped)

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/video-editor/projects` | List org projects (filter `?status=`) / create a project (`title`, `timeline`, optional `channelWorkspaceId`, `videoProjectId`, `canvasId`) |
| GET/PUT/DELETE | `/video-editor/projects/[id]` | Read / full-update (timeline + settings re-validated) / soft-delete a project |
| POST | `/video-editor/projects/[id]/render` | Validate timeline + media refs, estimate & charge Creative Canvas credits, dispatch a render job (`queued`→`dispatched`); 402 if credits insufficient |
| POST | `/video-editor/projects/[id]/reframe` | Clone the project as a new 9:16 variant, re-flowing clips using each upload's stored focus track; 400 if already 9:16 |
| POST | `/video-editor/projects/[id]/captions/generate` | Build/replace a caption track from a **completed** transcript's segments (`stylePreset`, `animationPreset`) |
| POST | `/video-editor/projects/[id]/tts` | Multi-section TTS voiceover (gateway `openai_audio` or BYOK ElevenLabs/OpenAI-compatible); writes audio clips to a track **and** a linked transcript so captions never desync |
| GET | `/video-editor/render-jobs?projectId=` | List render jobs for a project |
| GET/PUT | `/video-editor/render-jobs/[id]` | Read a job / render-runtime status callback (`rendering`\|`rendered`\|`failed`\|`cancelled`; `rendered` requires `output.url`+`output.storagePath` and registers outputs back onto the project; failure auto-refunds charged credits) |
| GET/POST | `/video-editor/transcripts?projectId=` | List a project's transcripts / dispatch a transcription job for a `clipId` or the project's last render |
| GET/PUT/DELETE | `/video-editor/transcripts/[id]` | Read / transcription-runtime callback (`processing`\|`completed`\|`failed`, refunds on failure) / soft-delete |
| POST | `/video-editor/transcripts/[id]/translate` | LLM-translate a **completed** transcript's segments into a new transcript (`language` required) |
| GET | `/video-editor/tts/voices?orgId=` | List OpenAI TTS voices + the org's BYOK ElevenLabs voices (if connected) |
| GET/POST/PUT | `/video-editor/media/[id]/beats?orgId=` | Read stored beat markers/BPM for an upload / dispatch beat analysis / analysis-runtime callback (`analyzed`\|`failed`) |
| GET | `/video-editor/stock/search?q=&kind=&page=` | Search Pexels + Pixabay in parallel (10-minute in-memory cache; `kind`: `image`\|`video`\|`all`) |
| POST | `/video-editor/stock/import` | Download an allow-listed stock result (`result` object from search) into org uploads (max 50MB, redirect-validated) |
| GET/POST | `/video-editor/luts?orgId=` | List org LUTs / upload a validated `.cube` file (multipart form, max 8MB) |
| DELETE | `/video-editor/luts/[id]` | Soft-delete a LUT |
| GET/POST | `/video-editor/templates?orgId=&category=` | List org + platform templates / create a template (platform templates require `role=admin` and cannot reference tenant media) |
| GET/PUT/DELETE | `/video-editor/templates/[id]` | Read / update / soft-delete a template (platform templates: admin-only writes) |
| POST | `/video-editor/templates/[id]/resolve` | Resolve a template's timeline fragment against the org's brand profile / settings / optional YouTube channel title |
| GET/POST | `/video-editor/media-previews?orgId=` | Fetch cached previews by `keys=` (comma-separated media keys, LRU-touches the proxy ledger) / `POST` to ensure previews exist for up to 50 media refs |
| GET/PUT | `/video-editor/media-previews/[id]` | Read a preview / preview-runtime callback reporting `status`, `waveform`, `filmstrip`, `proxy` (writing `proxy` also upserts a proxy-ledger entry) |
| GET | `/video-editor/proxy-ledger?orgId=` | List proxy cache entries (oldest-accessed first) + total bytes |
| DELETE | `/video-editor/proxy-ledger/[id]` | Evict a proxy: deletes the storage object, clears the preview's `proxy` field, deletes the ledger entry |

## Agent patterns

### Create project → render → poll job → confirm
1. `POST /video-editor/projects` with `{ orgId, title, timeline }` → capture `id`.
2. `GET /video-editor/projects/[id]` — read back and assert the title/timeline match what was sent before reporting "created."
3. `POST /video-editor/projects/[id]/render` → capture `jobId`. A 402 means insufficient org credits — report the exact required amount, don't retry silently.
4. Poll `GET /video-editor/render-jobs/[id]` until `status` is `rendered` (has `output.url`) or `failed`/`cancelled`. Never report a render as done without this read-back — the render runtime writes status asynchronously via the `PUT` callback, not the initial `POST`.

### Transcribe → generate captions → verify
1. `POST /video-editor/transcripts` with `{ projectId }` (or `clipId`) → capture `transcriptId`. 400 if the timeline has no render yet (whole-timeline transcription needs `lastRender.url`).
2. Poll `GET /video-editor/transcripts/[id]` until `status: completed` (has `segments`).
3. `POST /video-editor/projects/[id]/captions/generate` with `{ transcriptId }` → response includes `cueCount`; then `GET /video-editor/projects/[id]` to confirm the caption track landed in `timeline.tracks`.

### TTS voiceover (self-verifying)
`POST /video-editor/projects/[id]/tts` already writes both the audio clips onto a track **and** a matching transcript in one call — response has `transcriptId` and `trackId`. Still `GET` the project afterward to confirm the track exists before telling the human it's done; a 503 means no TTS provider is configured (gateway key or BYOK).

## Success gate

After any create/update/dispatch above:
1. `GET` the resource (project, job, transcript, template, LUT list) by id.
2. Assert the field you changed actually changed, or — for async dispatches (render, transcribe, beats, TTS) — that a job/transcript id exists and eventually reaches a terminal status.
3. Surface exact API `error` strings on 4xx/402/503 — do not retry with a different key or fake a completed status.

## Source of truth

Route implementations live under `app/api/v1/video-editor/**`. Credit accounting lives in `lib/creative-canvas/credits.ts` and `lib/video-editor/credits.ts`. If this skill and the route disagree, the route wins — update this skill immediately.

## Cross-references

- `content-engine` — short-form video production pipeline that feeds editor projects
- `youtube-studio-ops` — publish rendered video to YouTube; shares `channelWorkspaceId`/`videoProjectId` linkage
- `creative-canvas-ops` — canvas-driven exports, BYOK provider connections, and the shared credit ledger
