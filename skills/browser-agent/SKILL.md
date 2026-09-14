---
name: browser-agent
description: >
  Drive a real browser on the user's linked computer from inside Messages —
  open a page in the workbench browser tab, read it as an accessibility-tree
  text snapshot with stable @eN refs, click/type by ref, handle JS dialogs,
  read console errors, and (slice 2) attach to the page the user is already
  looking at. Use whenever the user says "open a page", "look at this site",
  "browse to …", "what's on this page", "click the …", or asks you to inspect,
  fill, or operate a webpage the user can see in their workbench.
---

# Browser Agent — Partners in Biz Workbench Browser

Hermes-Desktop-class browser capability inside Messages. The device-side
headless Chrome runs on the user's linked computer over loopback CDP; the
platform is the control plane; the workbench browser tab is the display
surface. The agent reads pages as **text snapshots** (accessibility trees with
stable `@eN` refs) — no vision model needed.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages
(`Authorization: Bearer pib_dlg_…`) plus `X-Org-Id: <orgId>`.

- Prefer the injected delegation token for all `/api/v1/*` calls in a
  human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Every agent browser call MUST send the header `X-Agent-Actor: sage` (any
  non-empty value). This is how the platform knows the request is agent-initiated:
  it triggers the private-network guard, driver arbitration, and agent-initiated
  session defaults. Without it the platform treats you as the human.
- Never claim a write succeeded without read-back.
- See skill `system-auth` for mint/resolve rules.

## Base URL & Conversation scoping

```
https://partnersinbiz.online/api/v1
```

All browser routes are conversation-scoped and session-scoped:

```
/api/v1/conversations/{conversationId}/workbench/browser/sessions
/api/v1/conversations/{conversationId}/workbench/browser/sessions/{sessionId}/...
```

`conversationId` comes from the run context (the conversation you are working
in). `sessionId` comes from the create response (field `sessionId`). The
binding (device/runtime) is derived server-side from the conversation — never
pass device ids.

## Tool surface

### browser_open — create a session (the tab appears beside the chat)

```
POST /api/v1/conversations/{conversationId}/workbench/browser/sessions
Headers: Authorization: Bearer <delegation> · X-Org-Id: <orgId> · X-Agent-Actor: sage
Body: { "startUrl": "https://news.ycombinator.com" }   # optional
```

Returns `202` with the public session. Agent-created sessions always start
`awaiting_approval` — the human must Approve in the workbench browser tab
before any page loads (a real browser reaching the internet from the user's
computer is sensitive). After creating, tell the user the browser tab opened
and ask them to Approve. Poll the session (GET .../sessions/{id}) or the
snapshot until `status: 'running'`.

Rules:
- `startUrl` must be http(s) with no embedded credentials.
- Agent sessions default `allowPrivateNetwork: false` — you cannot navigate to
  localhost / 192.168.x / 10.x / *.local unless the human flips the
  allow-private toggle. Never attempt to self-grant; the route rejects it.

### browser_snapshot — read the page as text (the agent's eyes)

Request a fresh snapshot (the device rebuilds it from the live page):

```
POST /api/v1/conversations/{conversationId}/workbench/browser/sessions/{sessionId}/snapshot
```

Then read it back (poll until `seq` advances past your previous seq):

```
GET  /api/v1/conversations/{conversationId}/workbench/browser/sessions/{sessionId}/snapshot
```

Response shape:

```
{ snapshot: {
    url, title,
    ax: "…text lines with [@e1] [@e2] refs…",
    refs: { "@e1": { backendDOMNodeId, role, name } },
    pendingDialog: { type, message } | null,
    frames: [ { frameId, parentId, url, name } ],
    console: [ { level, text, url, line } ]   // tail, newest first
  }, seq, atMs, status }
```

Read the `ax` text first. It is the page rendered as an accessibility tree —
every actionable element has a stable `@eN` ref. The snapshot also merges the
CDP supervisor state: pending native dialogs, the frame tree (including
cross-origin iframes), and recent console errors. If `pendingDialog` is set,
handle it with browser_dialog before clicking.

### browser_navigate

```
POST .../sessions/{sessionId}/navigate   Body: { "url": "https://…" }
```

Private/internal hosts are rejected for agent actors unless the session has
`allowPrivateNetwork: true` (human-granted). Take a fresh snapshot after
navigating — the page changed.

### browser_click_ref — click by accessibility ref

```
POST .../sessions/{sessionId}/click-ref   Body: { "ref": "@e1" }
```

Use refs from the most recent snapshot only — refs are per-snapshot. The
device resolves the ref to real coordinates and clicks. If the ref is stale,
take a new snapshot first.

### browser_type / browser_press / browser_scroll

```
POST .../sessions/{sessionId}/type     Body: { "text": "…" }
POST .../sessions/{sessionId}/press    Body: { "key": "Enter" }
POST .../sessions/{sessionId}/scroll   Body: { "x": 0, "y": 0, "deltaY": 400 }
```

`type` types into the focused element (click the field first via click-ref).
Allowed keys: Enter, Escape, Tab, Backspace, Delete, ArrowUp/Down/Left/Right,
Home, End, PageUp, PageDown.

### browser_dialog — respond to a native JS dialog

```
POST .../sessions/{sessionId}/dialog    Body: { "accept": true }  # or { "accept": false, "promptText": "…" }
```

Only meaningful when the latest snapshot shows `pendingDialog`. The agent may
quietly accept/dismiss — the supervisor surface is the snapshot.

### browser_console — read the console ring

```
POST .../sessions/{sessionId}/console    # ask the device to publish the ring
GET  .../sessions/{sessionId}/console    # read: { entries: [{level,text,url,line}], seq, atMs, status }
```

Use when a page looks broken: console errors are the first-class signal.

### browser_attach — join a session the user is looking at (slice 2)

If the user is driving a workbench browser session and asks you to help with
"what we're both looking at", the session already exists with
`initiator: 'user'`. List/find the session, take a snapshot to see the same
page state, and only drive after you hold the wheel.

### browser_take_control — driver arbitration

```
POST .../sessions/{sessionId}/driver    Body: { "driver": "agent" }
```

- The user and the agent must never click/type the same live page at the same
  time. Only one `driver` (user or agent) owns the wheel.
- Read-only calls (snapshot/console) are always allowed — watching is free.
- A driving control from the non-owner is rejected `409` with a clear message.
- **You cannot seize the wheel from an active human driver** — the route
  rejects it. If you need to drive, tell the user "I need control of the
  browser to act — click Take control" or wait until they release.
- When the human clicks Take control while you drive, the session driver
  flips to user; your next driving control gets 409 — take a snapshot to
  confirm, then wait or ask.

## Workflow: "open a page and tell me about it"

1. `browser_open` with the URL (or no URL, then navigate). Tell the user the
   tab opened and they need to Approve. Wait for approval (poll session status
   until `running`).
2. `browser_snapshot` (POST then GET, poll until seq advances). Read `ax`.
3. Report: page title/URL, what's on the page (from the AX text), any pending
   dialog or console errors. Quote real snapshot content — never invent page
   contents you did not read.
4. If the user asks you to act (click the search box, fill the form):
   click-ref the element, type, press Enter, snapshot again to verify the
   result. Verify your own actions with a follow-up snapshot.

## Workflow: "look at what I'm looking at" (shared page)

1. Find the running user session (list sessions for the conversation, or ask).
2. `browser_snapshot` to see the same page the user sees.
3. Read-only analysis is free (snapshot/console). To act: check `driver`; if
   `user`, tell them you need the wheel (Take control), or ask them to release.
4. After acting, verify with a snapshot and report what changed.

## Guardrails

- **Approval gate**: a session that starts `awaiting_approval` needs the human
  to Approve in the tab. Never claim you opened a page until the session is
  `running`.
- **Private network**: you cannot reach localhost/RFC1918/*.local without the
  human's explicit allow-private toggle. If blocked, say exactly that and ask
  them to flip it.
- **Redaction**: snapshot and console text are scrubbed server-side before you
  see them (passwords, tokens, API keys, bearer tokens). If a page you drive
  contains credentials, you will see `[redacted]` — do not ask the user to
  paste the secret; work around it by not needing it.
- **Never fabricate page state.** Every claim about a page must come from a
  snapshot you actually read. If a snapshot fails or the session is not
  running, say so.
- **Driver etiquette (slice 2)**: read-only is always fine; driving requires
  the wheel. Respect the human's Take control — do not fight for the wheel.
- **Do not** use the workbench browser for actions that belong to proper
  platform modules (research, CRM, documents). It is for browsing and
  inspecting web pages, not as a general-purpose API bypass.

## Verification contract

- After `browser_open`: GET the session — must be `status: 'running'` (after
  human approval) with a `currentPageUrl`.
- After `browser_navigate` / `browser_click_ref` / `browser_type`: take a new
  snapshot and confirm the page state changed as expected.
- After `browser_dialog`: snapshot again — `pendingDialog` must be null.
- Report sessions by id and page URL so the human can see the same tab.

## Implementation notes (for maintainers)

- Device: runtime-installers/runtime/workbench-browser.ts — CDP supervisor
  (pendingDialog, consoleRing capped 50, frameTree incl. OOPIFs via
  Target.setAutoAttach), AX snapshot builder, click_ref -> backendDOMNodeId ->
  box model -> center, redaction.
- Control plane: lib/messages/workbench/browser-sessions.ts (sanitizers,
  private-URL guard, driving-control set, X-Agent-Actor header), browser-session-store.ts
  (driver arbitration + private guard in enqueueControl).
- Routes: app/api/v1/conversations/[convId]/workbench/browser/sessions/**.
- Client: AgentWorkbenchRail -> WorkbenchBrowserPanel (agent view, driver
  badge, Take control, allow-private toggle).
- Spec: docs/specs/agent-aware-workbench-browser-2026-08-05.md.
