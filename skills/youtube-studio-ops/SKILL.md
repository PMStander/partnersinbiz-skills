---
name: youtube-studio-ops
description: >
  YouTube Studio module on Partners in Biz: channels, videos, release plans, clip
  candidates, publish packets, and the Creative Canvas production bridge (open-in-canvas
  seeding, automatic sync-back on completed canvas runs, export auto-create, scheduled
  publishing cron with approval gates, render imports into the canvas source library).
  Owner: maya. Use this skill whenever the user mentions YouTube Studio, channel linking,
  video release plans, or clip/repurpose workflows.
---

# YouTube Studio Ops — Partners in Biz Platform API

YouTube channel + video production/release pipeline: channel adoption/linking, source assets, video import/repurpose, render jobs, clip candidates, production drafts, release plans (with publish action), publish packets, series, analytics, and agent jobs — plus the Creative Canvas production bridge documented below.

## Owner & scope

- Owner: `maya`
- Scope: YouTube channel + video production/release pipeline: channel adoption/linking, source assets, video import/repurpose, render jobs, clip candidates, production drafts, release plans (with publish action), publish packets, series, analytics, and agent jobs.
- Base path: `https://partnersinbiz.online/api/v1/youtube-studio`

## Related skills

- `creative-canvas-ops` — open-in-canvas video editing, sync-back, exports
- `video-editor-ops` — source render pipeline
- `social-media-manager` — cross-post repurposed clips
- `content-engine`

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Creative Canvas bridge

Turns a YouTube Studio video project into a fully seeded Creative Canvas production board, keeps the two in sync as canvas runs complete, and lets a canvas export create — and later publish — the video project on its own.

### `POST /youtube-studio/videos/{id}/open-in-canvas?orgId=...` — auth: client

Opens (or creates) the canvas for a video project. Idempotent — calling it again on an already-linked video returns the existing canvas instead of creating a duplicate.

Response: `{ "canvasId": "canvas_abc", "created": true }` (201 if a canvas was just created, 200 if one already existed).

```bash
curl -X POST "https://partnersinbiz.online/api/v1/youtube-studio/videos/vid_123/open-in-canvas?orgId=org_abc" \
  -H "Authorization: Bearer $AI_API_KEY"
```

What gets seeded, from the video project's latest production draft:
- A brief node summarizing the video.
- One prompt node, one music-bed-audio node, and one video generator node per scene.
- A final assembly node with `edit.outputKind: "youtube_render"`, which is what the sync-back logic (below) watches for.

Note: seeded audio nodes are **music beds only** — there is no TTS model wired up yet, so scene narration is not auto-voiced. The narration script is preserved as text on each scene's prompt node so it isn't lost, it just isn't rendered to audio automatically.

Two-way link stored on both records: `video.creativeCanvasId` ↔ `canvas.linked.youtubeVideoProjectId`.

### Sync-back (automatic, no endpoint to call)

Once a video is linked, completed runs on that canvas write back to the video project automatically:

- **Any** completed video run on the linked canvas adds a `rendered_video` source asset to the video project, keyed `canvas-run-{runId}` (idempotent — re-processing the same run never double-adds it).
- A completed run on the node carrying `edit.outputKind: "youtube_render"` additionally flips the video's open render job to `rendered` (creating one if none exists), stamped with `renderEngine: { "provider": "creative_canvas", "jobId": "<runId>" }`.
- Approval and publish state on the video project are never touched by sync-back — a canvas render completing does not itself approve or schedule anything.

### Export auto-create (canvas → new video project)

Exporting a canvas node with target `youtube_studio` no longer requires the canvas to already be linked to a video project — it will auto-create one:

- Org has exactly **one** YouTube channel workspace → auto-creates against it, no extra input needed.
- Org has **several** channel workspaces → pass `channelWorkspaceId` in the export body to disambiguate.
- Org has **none** → 400 asking the caller to create a channel workspace first.

```bash
curl -X POST "https://partnersinbiz.online/api/v1/creative-canvas/canvas_abc/exports/draft?orgId=org_abc" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "nodeId": "node_final_assembly",
    "target": "youtube_studio",
    "channelWorkspaceId": "chw_marketing"
  }'
```

### Scheduled publishing (cron)

Release plans using an API publish mode with `scheduledPublishAt` are executed by a 5-minute cron, `GET /cron/youtube-studio-publish`:

- Every run re-checks all approval and readiness gates before publishing — nothing bypasses approval just because it's scheduled.
- Approval blocks never burn a retry attempt.
- Genuine publish failures are capped at 3 attempts, tracked via `publishAttemptCount` and `lastPublishError` on the plan.
- After 3 failed attempts the plan is marked terminal: `publishExecutionStatus: "failed"`, surfaced on the plan for a human to intervene.
- An in-flight guard prevents overlapping cron ticks from double-publishing the same plan.

### Render imports into the canvas source library

`youtube_render_jobs` whose status is `rendered`, `qa_review`, or `approved` — and which have an http(s) output URL — appear as importable sources in the Creative Canvas source library. Portal (client) users only see jobs whose visibility flags allow client viewing; internal-only render jobs stay invisible to them.

## API routes to document next

- `GET/POST /youtube-studio/channels`
- `GET/PATCH /youtube-studio/channels/[id]`
- `POST /youtube-studio/channels/adopt`
- `GET/POST /youtube-studio/channels/links`
- `GET/POST /youtube-studio/videos`
- `GET/PATCH /youtube-studio/videos/[id]`
- `POST /youtube-studio/videos/import`
- `POST /youtube-studio/videos/[id]/repurpose`
- `GET/POST /youtube-studio/source-assets`
- `GET/POST /youtube-studio/render-jobs`
- `GET/POST /youtube-studio/clip-candidates`
- `GET/POST /youtube-studio/production-drafts`
- `GET/POST /youtube-studio/release-plans`
- `POST /youtube-studio/release-plans/[id]/publish`
- `GET/POST /youtube-studio/publish-packets`
- `GET/POST /youtube-studio/series`
- `GET /youtube-studio/analytics`
- `POST /youtube-studio/analytics/ingest`
- `GET/POST /youtube-studio/agent-jobs`

## Next steps to un-stub this skill further

- Document request/response shapes and the auth level (`viewer`/`member`/`admin`/`system`/delegation-only) per remaining route above.
- Add an `## Agent patterns` / workflow-guide section once at least one end-to-end flow (import → repurpose → release plan → publish) has been run and verified (write → read-back → report).
- Register any newly-confirmed write-then-verify contract in the pack `verificationContract`.

## Cross-references

- video-editor-ops (source render pipeline)
- creative-canvas-ops (open-in-canvas)
- social-media-manager (cross-post repurposed clips)
- content-engine
