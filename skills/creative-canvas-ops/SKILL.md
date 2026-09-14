---
name: creative-canvas-ops
description: >
  Creative Canvas module on Partners in Biz: node graphs, generation runs, provider
  dispatch, exports to client documents/manuscripts/social drafts, collaborator presence,
  and bring-your-own-key (BYOK) provider connections (xAI, Google/Gemini, fal.ai, Recraft,
  Higgsfield) with the BYOK-vs-platform-credit billing resolution order. Owner: maya. Use
  this skill whenever the user mentions the Creative Canvas, canvas nodes, canvas runs,
  exporting a canvas node to a document/draft, or connecting a client's own AI provider key.
---

# Creative Canvas Ops — Partners in Biz Platform API

Node-graph based creative production surface: canvases, nodes, generation runs (with provider dispatch/retry), exports (client-document draft, manuscript, package, social draft), sharing/presence, source uploads, connections, and templates.

## Owner & scope

- Owner: `maya`
- Scope: Node-graph based creative production surface: canvases, nodes, generation runs (with provider dispatch/retry), exports (client-document draft, manuscript, package, social draft), sharing/presence, source uploads, connections, and templates.
- Base path: `https://partnersinbiz.online/api/v1/creative-canvas`

## Related skills

- `client-documents` (`canvas_draft` document type arrives via canvas exports/draft — do not create directly)
- `content-engine`
- `video-editor-ops`
- `book-studio-ops` (open-in-canvas)
- `youtube-studio-ops` (open-in-canvas)

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Creative provider connections (BYOK)

Bring-your-own-key connections for the Creative Canvas. Lets a client wire up their own xAI, Google (Gemini), fal.ai, Recraft, or Higgsfield credentials so canvas generation runs on their account instead of platform credits. All routes: auth `client`, `orgId` via `?orgId=` query or `x-org-id` header (falls back to `user.orgId`/`orgIds[0]`).

Providers that support connections: `xai`, `google`, `fal`, `recraft`, `higgsfield` (Higgsfield needs `apiKey` + `apiSecret`; the rest just `apiKey`).

### `GET /creative-canvas/connections?orgId=...` — auth: client
Lists the caller's own user-scoped connections plus the org's org-scoped connections. Always masked — no `credentialsEnc`, only `credentialHint` (e.g. `xai-…1234`) and `hasCredentials`.

Response:
```json
{ "connections": [
  { "id": "org:org_abc:xai", "provider": "xai", "scope": "org", "orgId": "org_abc",
    "ownerUid": null, "label": "xAI (Grok)", "status": "connected",
    "credentialHint": "xai-…1234", "hasCredentials": true,
    "lastValidatedAt": "...", "lastUsedAt": "...", "lastError": null }
] }
```

### `POST /creative-canvas/connections?orgId=...` — auth: client
Body:
```json
{ "provider": "xai", "scope": "org", "label": "Marketing xAI key",
  "credentials": { "apiKey": "xai-..." } }
```
For Higgsfield, `credentials` needs both `apiKey` and `apiSecret`.

- `scope`: `"org"` (shared by everyone in the org) or `"user"` (portable across all orgs the calling user belongs to). **Agents (`role: "ai"`) can only create org-scoped connections** — `scope: "user"` from an agent caller returns 400 `Agents can only create organisation-scoped connections`.
- The key is validated against the provider before it's stored — a bad/expired key returns 400 with the provider's validation error, nothing is persisted.
- Credentials are AES-256-GCM encrypted, keyed off `org:{orgId}` or `user:{uid}` (org and user connections can never decrypt each other's blobs).
- Connection id is derived as `org:{orgId}:{provider}` or `user:{uid}:{provider}` — URL-encode the colons when addressing `/connections/{id}`.
- Errors: 400 `scope must be "org" or "user"`, 400 `credentials are required`, 400 `Credential value too long` (>4096 chars), 400 `<Field> is required` for missing required fields, 400 `Provider does not support connections` for providers without a `connection` config (e.g. `manual_upload`, `agent_task`).
- Success: 201 `{ "connection": { ...masked } }`.

### `DELETE /creative-canvas/connections/{id}?orgId=...` — auth: client
Revokes the connection (clears stored credentials, `status` → `revoked`). Errors: 403 `Forbidden`, 404 `Connection not found`. Success: `{ "connection": { ...masked } }`.

### `POST /creative-canvas/connections/{id}/validate?orgId=...` — auth: client
Re-checks a stored key against the provider and updates `status`/`lastValidatedAt`/`lastError`. Response: `{ "connection": { ...masked }, "validation": { "ok": true } }` (or `{ "ok": false, "error": "..." }`). 400 `Connection has no stored credentials` if already revoked.

### BYOK billing rule

When generating on the canvas, credential resolution runs **user-scoped connection → org-scoped connection → shared platform runtime → `connection_required`**:

- If a usable connection is found (user-scoped wins over org-scoped), the run is billed to the user's own provider account — run provenance is stamped `{ "costUnits": 0, "costLabel": "byok:<provider>" }` and it **bypasses platform creative-canvas credits entirely**.
- `higgsfield` always has a shared-runtime fallback (unchanged behaviour — the existing VPS Higgsfield executor, billed in platform credits) even with no connection configured.
- `xai` falls back to the platform `XAI_API_KEY` env var if no connection exists (still charges platform credits).
- `google`, `fal`, and `recraft` have **no shared fallback** — generating with one of their models and no connection returns 400 `Connect a <provider> account in Creative providers to use this model`.

### New canvas models (BYOK direct lane)

These model ids run against the connected provider directly (not through the Higgsfield executor):

| Model id | Provider | Kind | Execution |
|---|---|---|---|
| `grok-imagine-image` | xai | image | sync |
| `grok-imagine-image-quality` | xai | image | sync |
| `grok-imagine-video` | xai | video | async |
| `grok-imagine-video-1.5` | xai | video | async |
| `gemini-3-pro-image-preview` | google | image | sync |
| `imagen-4` | google | image | sync |
| `recraftv4` | recraft | image | sync |
| `recraftv4-vector` | recraft | image | sync |
| `fal-flux-2-pro` | fal | image | async |
| `fal-kling-video-2-6-pro` | fal | video | async |
| `fal-veo-3-1` | fal | video | async |

`google`, `recraft`, and `fal` models always require a connection (no platform fallback). `xai` models fall back to the platform key if unconnected. Async models are dispatched via the direct-provider runtime (submit + poll against the provider's own API) rather than the shared Higgsfield job queue.

## API routes to document next

- `GET/POST /creative-canvas`
- `GET/PATCH /creative-canvas/[id]`
- `GET /creative-canvas/[id]/graph`
- `GET/POST /creative-canvas/[id]/nodes/[nodeId]/output`
- `POST /creative-canvas/[id]/nodes/[nodeId]/review`
- `GET/POST /creative-canvas/[id]/runs`
- `POST /creative-canvas/[id]/runs/generate`
- `POST /creative-canvas/[id]/runs/retry`
- `POST /creative-canvas/[id]/runs/[runId]/complete`
- `POST /creative-canvas/[id]/runs/[runId]/provider-dispatch`
- `GET /creative-canvas/[id]/runs/[runId]/provider-status`
- `POST /creative-canvas/[id]/runs/[runId]/retry`
- `POST /creative-canvas/[id]/exports/draft (client_document/blog_post target — see client-documents `canvas_draft` type)`
- `POST /creative-canvas/[id]/exports/manuscript`
- `POST /creative-canvas/[id]/exports/package`
- `POST /creative-canvas/[id]/exports/social-draft`
- `GET/POST /creative-canvas/[id]/comments`
- `GET/POST /creative-canvas/[id]/versions`
- `POST /creative-canvas/[id]/share`
- `GET/POST /creative-canvas/[id]/presence`
- `POST /creative-canvas/[id]/presence/events`
- `GET/POST /creative-canvas/[id]/orchestration-tasks`
- `GET /creative-canvas/credits`
- `POST /creative-canvas/import/campaign`
- `GET/POST /creative-canvas/sources`
- `POST /creative-canvas/sources/upload`
- `GET/POST /creative-canvas/templates`
- `POST /creative-canvas/provider-callbacks/higgsfield (provider webhook, not agent-called)`

## Next steps to un-stub this skill further

- Document request/response shapes and the auth level (`viewer`/`member`/`admin`/`system`/delegation-only) per remaining route above.
- Add copy-paste-ready example payloads once shapes are confirmed against route source.
- Add an `## Agent patterns` / workflow-guide section once at least one end-to-end flow has been run and verified (write → read-back → report).
- Register any newly-confirmed write-then-verify contract in the pack `verificationContract`.

## Cross-references

- client-documents (`canvas_draft` document type arrives via canvas exports/draft — do not create directly)
- content-engine
- video-editor-ops
- book-studio-ops (open-in-canvas)
- youtube-studio-ops (open-in-canvas)
