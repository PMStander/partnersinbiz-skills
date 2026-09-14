---
name: google-workspace
description: >
  Store, retrieve, share, and manage binary artifacts (images, videos, PDFs, brand kits, ad creatives,
  reports, contracts, and any non-text file) using Google Drive, Google Docs, and Google Sheets through
  the Partners in Biz platform. Use this skill whenever the user or another agent mentions anything
  related to binary file storage or sharing, including but not limited to: "upload to drive",
  "save to drive", "save this to Drive", "put it in Drive", "share with client", "send the report",
  "create a Google Doc", "open a Google Doc", "save the video", "upload the brand kit",
  "client deliverable", "send the deliverable", "drive folder", "shared drive", "ad creative",
  "marketing asset", "where do I save this image", "store this PDF", "upload this file",
  "save the brand kit", "brand folder", "upload the creative", "save the ad", "where does this go",
  "give the client access", "share a link", "viewer link", "download the report", "export to Drive",
  "save to Google", "google sheet", "append to sheet", "update the spreadsheet", "log this to sheets",
  "read from sheets", "brand kit folder", "client folder", "deliverables folder", "raw sources folder",
  "find that file in Drive", "search Drive", "Drive search", "Drive link", "get the Drive URL",
  "artifact", "generate and save", "produce and deliver", "produce a report", "marketing deliverable",
  "save the social pack", "upload the social pack", "send the video to the client",
  "share the images", "share the PDF", "where do binary files go", "asset storage". If in doubt,
  trigger — this skill governs ALL binary artifact storage across the Cowork ecosystem.
---

# Google Workspace — Binary Artifact Storage

This skill governs how agents store, retrieve, and share **binary artifacts** — images, videos, PDFs,
brand kits, ad creatives, reports, contracts, and any other non-text file generated during client
work. Text knowledge (specs, briefs, research, plans) lives in Obsidian. Code lives in GitHub.
Everything else lives in Google Drive.

## The Three-Tier Rule

Get the file type right or it ends up invisible to other agents and to the client.

| File type | Canonical location | Why |
|---|---|---|
| Specs, plans, briefs, research dumps, architecture docs | `~/Cowork/Cowork/agents/<domain>/wiki/` | Obsidian syncs to VPS + mobile; searchable by all agents |
| Code, READMEs, ADRs, in-tree config, skill files | Project git repo | Version-controlled; not synced to Obsidian or Drive |
| **Binary artifacts** — images, videos, PDFs, brand kits, ad creatives, signed contracts, invoices, renders, exports | **Google Drive** (`My Drive/Clients/<Client>/...`) | Drive is the canonical binary store; shareable directly with clients |

The full table and symlink rules live in `/Users/peetstander/Cowork/CLAUDE.md` under "Where to put agent-generated files". Read that if you're unsure about a file type.

**Rule of thumb:** if the file would corrupt in a markdown editor or break in a git diff, it goes to Drive.

---

## Per-Client Folder Convention

Every client gets a root folder under `My Drive/Clients/`. Use this structure exactly — the numbered
prefixes ensure stable sort order and predictable paths for programmatic access.

```
My Drive/
└── Clients/
    └── <Client Name>/          e.g. "Loyalty Plus", "AHS Law", "Lumen"
        ├── 01_brand/           logo files, font licences, brand kit PDF, colour palettes
        ├── 02_marketing/       ad creatives, video edits, social images, campaign packs
        │   └── <campaign>/     sub-folder per campaign, e.g. "black-friday-2026"
        ├── 03_deliverables/    final reports, signed contracts, invoices, strategy docs as PDF
        └── 04_raw-sources/     clipped PDFs, screenshots, datasets, reference files
```

### Discovering or creating a client folder

1. Call `drive_search` with `q: "<Client Name>"` and a known parent `folderId` when available to find the root.
2. If it exists, use the returned folder ID for all child operations.
3. If it does not exist, ask Peet/operator for the correct client folder or create folders through Workspace Broker (`POST /workspace-broker/folders/create`) when that task is approved. Do not try to create folders with `drive_upload`; the direct upload endpoint uploads files only.
4. Always use the folder **ID** (not the path string) for subsequent operations — paths are not stable across renames.

---

## Operations

These are the tool contracts agents call through the PiB platform proxy. The direct proxy endpoints
are implemented in `partnersinbiz-web` on `development` as of 2026-06-15.

All calls require normal PiB API auth plus an org scope:

```bash
Authorization: Bearer $AI_API_KEY
X-Org-Id: <ORG_ID>
```

You may pass `orgId` in the query/body instead of `X-Org-Id`, but do not send conflicting org values.

### Active PiB agent workspace

The generic writable agent workspace is:

- Shared Drive: `PIB Shared Drive` (`0AMIddYkNl52sUk9PVA`)
- Folder: `PiB Agent Service Workspace` (`1bCGS5zntv2VEbDdZx0hVf-QrVCv3kvp8`)
- Service account: `workspace-agent@partners-in-biz-85059.iam.gserviceaccount.com`
- Folder role: `fileOrganizer`

Use folder ID `1bCGS5zntv2VEbDdZx0hVf-QrVCv3kvp8` for generic agent-generated Drive artifacts
when a more specific client folder has not been provided.

Do **not** target service-account uploads at `root` or an ordinary My Drive folder. Google blocks
service-account root/My Drive uploads with: `Service Accounts do not have storage quota`. Use a
Shared Drive folder or domain-wide delegation.

---

### `drive_list` — list files in a folder

```bash
curl -X GET \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: <ORG_ID>" \
  "https://partnersinbiz.online/api/v1/google/drive/list?folderId=<FOLDER_ID>&pageSize=50"
```

Query params:
- `orgId` or `X-Org-Id` (required)
- `folderId` (required) — Drive folder ID. Prefer explicit shared client folder IDs.
- `pageSize` — default 50, max 200
- `pageToken` — cursor for next page
- `includeFolders` — `true` to include folders; otherwise folders are hidden

Response:
```json
{
  "success": true,
  "data": {
    "files": [
      { "id": "1abc...", "name": "logo-v3.png", "mimeType": "image/png",
        "size": "204800", "webViewLink": "https://drive.google.com/...",
        "modifiedTime": "2026-05-13T10:00:00Z", "parents": ["folder_abc"] }
    ],
    "nextPageToken": "token_abc"
  }
}
```

---

### `drive_upload` — upload a local file to Drive

```bash
curl -X POST \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: <ORG_ID>" \
  -F "file=@/path/to/file.png" \
  -F "folderId=<FOLDER_ID>" \
  -F "name=logo-v3.png" \
  "https://partnersinbiz.online/api/v1/google/drive/upload"
```

Fields (multipart/form-data):
- `file` (required) — binary file, max 5 GB
- `folderId` (required) — destination folder ID
- `name` — override filename; defaults to original filename
- `mimeType` — override MIME type; defaults to uploaded file type or `application/octet-stream`

JSON upload is also supported for small generated text artifacts:
```json
{ "orgId": "org_abc", "folderId": "folder_abc", "name": "notes.txt", "mimeType": "text/plain", "content": "hello" }
```
Use `contentBase64` instead of `content` when binary bytes must travel through JSON.

Response (201):
```json
{
  "success": true,
  "data": {
    "id": "1abc...",
    "name": "logo-v3.png",
    "mimeType": "image/png",
    "webViewLink": "https://drive.google.com/file/d/1abc.../view",
    "parents": ["folder_abc"]
  }
}
```

Use `webViewLink` for sharing with humans. Use `drive_download` for programmatic download.

---

### `drive_download` — download a file by ID

```bash
curl -X GET \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: <ORG_ID>" \
  "https://partnersinbiz.online/api/v1/google/drive/download?fileId=<FILE_ID>" \
  -o output.png
```

Query params:
- `fileId` (required)
- `exportMimeType` — for Google Workspace files (Docs/Sheets/Slides), specify export MIME: `application/pdf`, `text/plain`, etc.

Response: raw binary stream with appropriate `Content-Type`.

---

### `drive_share` — share a file or folder with an email address

```bash
curl -X POST \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Org-Id: <ORG_ID>" \
  -d '{
    "fileId": "1abc...",
    "emailAddress": "client@example.com",
    "role": "reader",
    "sendNotificationEmail": true
  }' \
  "https://partnersinbiz.online/api/v1/google/drive/share"
```

Body fields:
- `fileId` (required)
- `emailAddress` (required) — recipient email
- `type` — `user` or `group`; defaults to `user`
- `role` — `reader` | `commenter` | `writer`; defaults to `reader`
- `sendNotificationEmail` — default `false`; set `true` to notify

Response:
```json
{ "success": true, "data": { "id": "perm_abc", "type": "user", "role": "reader", "emailAddress": "client@example.com" } }
```

The proxy deliberately rejects `type: "anyone"` public shares. Share folders or files only with
explicit users/groups unless Peet approves a different route.

---

### `drive_search` — full-text + filename search across Drive

```bash
curl -X GET \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: <ORG_ID>" \
  "https://partnersinbiz.online/api/v1/google/drive/search?q=brand+kit&folderId=<FOLDER_ID>"
```

Query params:
- `orgId` or `X-Org-Id` (required)
- `q` (required) — search string (searches filename and full text)
- `folderId` — restrict to a known shared folder ID
- `pageSize` — default 50, max 200
- `pageToken` — cursor for next page

Response: same shape as `drive_list`.

The `q` param is forwarded to the Drive API's `fullText contains` + `name contains` operator, OR'd together.

---

### `docs_create` — create a new Google Doc with optional content

```bash
curl -X POST \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Org-Id: <ORG_ID>" \
  -d '{
    "title": "Q3 Strategy Report — Loyalty Plus",
    "content": "# Q3 Strategy\n\n## Goals\n...",
    "folderId": "<FOLDER_ID>"
  }' \
  "https://partnersinbiz.online/api/v1/google/docs/create"
```

Body:
- `title` (required)
- `content` — optional plain text inserted at the top of the document
- `folderId` — where to place the Doc; if omitted, Google creates it in the service-account default root

Response (201):
```json
{ "success": true, "data": { "documentId": "1xyz...", "title": "Q3 Strategy Report — Loyalty Plus",
  "webViewLink": "https://docs.google.com/document/d/1xyz.../edit" } }
```

Use this when a deliverable is best consumed as a living Google Doc rather than a PDF. For
static exports, generate the Doc then use `drive_download` with `exportMimeType=application/pdf`.

---

### `sheets_append` — append a row to a Google Sheet

```bash
curl -X POST \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Org-Id: <ORG_ID>" \
  -d '{
    "spreadsheetId": "1abc...",
    "range": "Sheet1",
    "values": [["2026-05-13", "Loyalty Plus", "Black Friday Pack", "Done", "https://drive.google.com/..."]]
  }' \
  "https://partnersinbiz.online/api/v1/google/sheets/append"
```

Body:
- `spreadsheetId` (required)
- `range` (required) — sheet name or A1 range (e.g. `Sheet1`, `Deliverables!A:E`)
- `values` (required) — 2D array; each inner array is one row

Response:
```json
{ "success": true, "data": { "spreadsheetId": "1abc...", "updates": { "updatedRange": "Sheet1!A10:E10", "updatedRows": 1 } } }
```

---

### `sheets_read` — read a range from a Google Sheet

```bash
curl -X GET \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: <ORG_ID>" \
  "https://partnersinbiz.online/api/v1/google/sheets/read?spreadsheetId=1abc...&range=Sheet1!A1:E20"
```

Query params:
- `spreadsheetId` (required)
- `range` (required)

Response:
```json
{
  "success": true,
  "data": {
    "spreadsheetId": "1abc...",
    "range": "Sheet1!A1:E20",
    "values": [
      ["Date", "Client", "Asset", "Status", "Drive URL"],
      ["2026-05-13", "Loyalty Plus", "Black Friday Pack", "Done", "https://drive.google.com/..."]
    ]
  }
}
```

---

## Auth Model

**Current state: platform endpoints, credentials, and the generic Shared Drive target are active.**

Auth flows as follows:

- **Mac / Claude Code sessions:** service account JSON at `~/.config/gcloud/workspace-sa.json` is picked up by the PiB API. Agents never hold Drive credentials directly.
- **VPS (Hermes):** service account JSON at `/etc/hermes/google-drive-sa.json` (mode 600), used by `rclone` for direct Drive access and by the PiB API proxy when the VPS calls platform endpoints.
- **All agent calls go through the PiB platform:** `Bearer $AI_API_KEY` → `https://partnersinbiz.online/api/v1/google/...` → PiB API authenticates to Drive using the stored service account. Agents never handle OAuth tokens directly.
- **Env vars:** use `GOOGLE_WORKSPACE_CREDS_JSON_PATH` for Mac/VPS file paths and `GOOGLE_WORKSPACE_CREDS_JSON` for Vercel/serverless raw service-account JSON. Do not point Vercel at `/etc/hermes/...`; that file exists only on the VPS.

The service account must be granted access to specific client folders only — never the entire Drive.
For generic agent work, use `PiB Agent Service Workspace` in the Shared Drive. For client work, share
the specific client folder or campaign folder with the service account email. This is the least-privilege posture.

---

## When NOT to Use This Skill

| Situation | Use instead |
|---|---|
| Writing a spec, plan, brief, research dossier, or architecture doc | Obsidian — `~/Cowork/Cowork/agents/<domain>/wiki/` |
| Writing code, configs, or skill files | Git — commit to the project repo |
| Creating a short text summary of work done | Include inline in the kanban task's `agentOutput.summary` |
| Uploading a social post image to the PiB platform (not Drive) | `POST /api/v1/social/media/upload` via the social-media-manager skill |

Drive is for artifacts that need to be **shared with clients as files** or that are too large/binary for git or Obsidian. If it's text and it fits in a markdown file, it does not belong in Drive.

---

## Kanban Artifact Embed Pattern

When an agent generates a binary artifact and stores it in Drive, the Drive URL must be written back
to the kanban task so the Agent Board UI can surface it. Use the `agentOutput.artifacts` array on
the task PATCH:

```bash
PATCH /api/v1/projects/{projectId}/tasks/{taskId}
{
  "agentOutput": {
    "summary": "Generated 5 Black Friday social image variants and uploaded to Drive.",
    "artifacts": [
      { "type": "url", "ref": "https://drive.google.com/file/d/1abc.../view", "label": "Black Friday — Square v1" },
      { "type": "url", "ref": "https://drive.google.com/file/d/1xyz.../view", "label": "Black Friday — Stories v1" }
    ],
    "completedAt": "2026-05-13T10:00:00Z"
  },
  "agentStatus": "done"
}
```

Artifact schema: `{ type: 'url' | 'file' | 'commit' | 'message-thread' | 'doc', ref: string, label?: string }`.

The Agent Board UI renders `type: 'url'` artifacts as clickable links. Always label them clearly —
"Brand kit v3", "Q3 Report PDF", "Black Friday — Square 1024x1024" — so the human knows what
they're clicking before they open Drive.

---

## End-to-End Example — Social Pack for a Client

Maya is asked to "create a Black Friday social pack for Loyalty Plus":

1. **Generate assets** — Maya calls `higgsfield-generate` or `higgsfield-product-photoshoot` to produce 5 image variants.

2. **Find the client folder** — call `drive_search` with `q: "Loyalty Plus"` and a known parent folder ID if available. If none is found, ask Peet/operator for the correct shared folder or create it through Workspace Broker with approval.

3. **Upload each image** — call `drive_upload` once per image, targeting `Clients/Loyalty Plus/02_marketing/black-friday-2026/` by folder ID.

4. **Share with client** — call `drive_share` on the campaign sub-folder (not individual files) with `emailAddress: <client email>`, `role: 'reader'`, `sendNotificationEmail: true`. One share permission covers the whole campaign folder.

5. **Write back to kanban** — PATCH the task with `agentStatus: 'done'` and `agentOutput.artifacts` containing all 5 Drive view URLs. Include the folder share link as an additional artifact labeled "Campaign folder — Loyalty Plus Black Friday".

6. **Brief Peet or the operator** — surface the folder URL in your response so the human can see it without opening the kanban.

---

## VPS-Side Access

Hermes agents on `hermes-vps-01` (Helsinki, Hetzner CX23) access the same Drive via two paths:

- **PiB API proxy** — agents call `https://partnersinbiz.online/api/v1/google/...` with `Bearer $AI_API_KEY` exactly as Mac-side agents do. Same auth, same endpoints. Preferred for standard operations; production has `GOOGLE_WORKSPACE_CREDS_JSON` configured.
- **`rclone` remote** — VPS `gdrive:` is configured for the `hermes` user and can upload/read Drive files directly. Use this for VPS-local binary artifacts when the API proxy is blocked by missing Vercel Google credentials or when uploading large files from `/var/lib/hermes/outputs`.
- **Service-account `rclone` backend** — use the configless Drive backend with `/etc/hermes/google-drive-sa.json` and root folder `1bCGS5zntv2VEbDdZx0hVf-QrVCv3kvp8` when you need service-account CRUD from the VPS.

Both paths should target the same Drive workspace, but they use different credentials. Do not assume the
PiB API proxy is live just because `rclone` works, and do not assume the `hermes` user can use a root-only
rclone config. Verify from the agent user:

```bash
sudo -iu hermes bash -lc 'rclone about gdrive: >/dev/null && echo gdrive-ok'
```

For a VPS-local artifact upload:

```bash
sudo -iu hermes bash -lc '
  rclone copyto /var/lib/hermes/outputs/<run>/<file> "gdrive:PiB Agent Research/outputs/<run>/<file>"
  rclone link "gdrive:PiB Agent Research/outputs/<run>/<file>"
'
```

The verified 2026-06-15 system video path is:

```text
gdrive:PiB Agent Research/outputs/pib-system-video-2026-06-15/partners-in-biz-system.mp4
```

For service-account CRUD from the VPS as `hermes`:

```bash
remote=':drive,service_account_file=/etc/hermes/google-drive-sa.json,root_folder_id=1bCGS5zntv2VEbDdZx0hVf-QrVCv3kvp8:'

# Create
sudo -u hermes rclone copyto /tmp/artifact.txt "${remote}artifact.txt" --drive-use-trash=true

# Read
sudo -u hermes rclone cat "${remote}artifact.txt"

# Update/overwrite
sudo -u hermes rclone copyto /tmp/artifact-v2.txt "${remote}artifact.txt" --drive-use-trash=true

# Delete means trash for this Shared Drive folder role. Permanent hard-delete can require manager rights.
sudo -u hermes rclone deletefile "${remote}artifact.txt" --drive-use-trash=true
```

Verified from the VPS on 2026-06-15 as `hermes`: create readback `create-v1`, update readback
`update-v2`, and delete/trash confirmation `ok`.

---

## Operator Setup — Finish Credential Activation

The PiB API routes are implemented. Follow these steps to activate real Drive access if they have
not already been completed.

### Step 1 — GCP project

Use the existing GCP project `partners-in-biz-85059` or create a new one. If reusing, check that Drive/Docs/Sheets APIs are not already enabled before enabling them (avoids duplicate billing).

### Step 2 — Enable APIs

In the GCP console (or via `gcloud`):
```bash
gcloud services enable drive.googleapis.com docs.googleapis.com sheets.googleapis.com \
  --project=partners-in-biz-85059
```

### Step 3 — Create a service account

```bash
gcloud iam service-accounts create workspace-agent \
  --display-name="Hermes Workspace Agent" \
  --project=partners-in-biz-85059

gcloud iam service-accounts keys create workspace-sa.json \
  --iam-account=workspace-agent@partners-in-biz-85059.iam.gserviceaccount.com
```

Note the service account email — you will use it to share Drive folders.

### Step 4 — Place the key securely

- **Mac:** `cp workspace-sa.json ~/.config/gcloud/workspace-sa.json && chmod 600 ~/.config/gcloud/workspace-sa.json`
- **VPS:** `scp workspace-sa.json hermes-vps-01:/etc/hermes/google-drive-sa.json && ssh hermes-vps-01 chmod 600 /etc/hermes/google-drive-sa.json`
- Delete the local `workspace-sa.json` after copying — do not leave it in any git-tracked path.

### Step 5 — Share client folders with the service account

For each client, share their root Drive folder with the service account email and grant **Editor** role. Do this in the Google Drive web UI (or via the Drive API). Never share the entire Drive — folder-level sharing only.

Example:
```
Share "My Drive/Clients/Loyalty Plus" → workspace-agent@partners-in-biz-85059.iam.gserviceaccount.com → Editor
Share "My Drive/Clients/AHS Law"      → same email → Editor
```

### Step 6 — Set the env var

On Mac (`.env.local`):
```
GOOGLE_WORKSPACE_CREDS_JSON_PATH=/Users/peetstander/.config/gcloud/workspace-sa.json
```

On VPS profile/service env:
```bash
GOOGLE_WORKSPACE_CREDS_JSON_PATH=/etc/hermes/google-drive-sa.json
```

On Vercel, store the raw JSON as a secret env var:
```bash
printf "%s" "$(cat /secure/path/workspace-sa.json)" | vercel env add GOOGLE_WORKSPACE_CREDS_JSON preview
printf "%s" "$(cat /secure/path/workspace-sa.json)" | vercel env add GOOGLE_WORKSPACE_CREDS_JSON production
```

Use `vercel env ls` to verify the variable name exists. The value is encrypted and should not be printed.

### Step 7 — Configure rclone on VPS (optional but recommended)

```bash
# On hermes-vps-01
rclone config create gdrive drive \
  service_account_file=/etc/hermes/google-drive-sa.json \
  scope=drive
```

Test: `rclone ls gdrive:Clients/Loyalty\ Plus/01_brand/`

If `root` has a working `gdrive:` remote but `hermes` does not, copy only the rclone config file into
the hermes account with locked-down permissions:

```bash
install -d -m 700 -o hermes -g hermes /var/lib/hermes/.config/rclone
install -m 600 -o hermes -g hermes /root/.config/rclone/rclone.conf /var/lib/hermes/.config/rclone/rclone.conf
sudo -iu hermes bash -lc 'rclone about gdrive:'
```

### Step 8 — Smoke test

```bash
# Upload a test file
curl -X POST -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: <ORG_ID>" \
  -F "file=@/tmp/test.txt" \
  -F "folderId=<SHARED_FOLDER_ID>" \
  -F "name=drive-integration-test.txt" \
  "https://partnersinbiz.online/api/v1/google/drive/upload"

# List the same shared folder
curl -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: <ORG_ID>" \
  "https://partnersinbiz.online/api/v1/google/drive/list?folderId=<SHARED_FOLDER_ID>"
```

If both return 200, the integration is live. Delete the test file and update this section.

---

## Agent Patterns

1. **Search before creating** — always call `drive_search` to check if a client folder exists before creating a new one. Duplicate folders are hard to clean up at scale.
2. **Share folders, not files** — when giving a client access to a campaign, share the campaign sub-folder. Individual file shares create noise in Drive and are harder to revoke.
3. **Name files with version and date** — `brand-kit-v3-2026-05.pdf` not `brand-kit-final-FINAL.pdf`. Clients rename things; the version in the filename is the source of truth.
4. **Always write artifacts to kanban** — a Drive URL that isn't in `agentOutput.artifacts` is invisible to Peet and to other agents. Never skip this step.
5. **Binary artifacts = Drive; text knowledge = Research/Obsidian** — if you're tempted to put a markdown file in Drive, stop. Working client research belongs in the Research module first, then selected durable summaries can be exported to the wiki.
