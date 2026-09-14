---
name: research-intelligence
description: >
  Use when creating, updating, citing, reviewing, exporting, or converting
  Partners in Biz Research records for prospects, clients, campaigns, SEO,
  CRM, ads, onboarding, internal decisions, and client-visible evidence.
---

# Research Intelligence — Partners in Biz

Research is the source of truth for working evidence before it becomes a polished client document, project task, campaign decision, CRM action, SEO recommendation, or durable knowledge note.

Use this skill whenever work needs to answer "what is true?", "what evidence supports this?", "what is still unknown?", or "what should we recommend next?".

## Platform Surface

Base URL: `/api/v1`

Authentication:
- Admin Research routes use `withAuth('admin')` and `resolveOrgScope`.
- Portal Research routes use `withPortalAuthAndRole('viewer')` and only expose `client_visible` records for the active portal org.
- Agents acting with Peet/admin access may create and edit Research. Client users may view and comment only on visible records.

UI routes:
- `/portal/research`
- `/portal/research/[id]`
- `/admin/org/[slug]/research`
- `/admin/org/[slug]/research/[id]`
- `/portal/research`
- `/portal/research/[id]`

## API Reference

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/research` | List active Research items for the resolved org. Supports `orgId`, `kind`, `status`, `visibility`, and `q`. |
| `POST` | `/research` | Create a Research item. Requires `title`; accepts `orgId`, `kind`, `status`, `visibility`, `summary`, `notesMarkdown`, `tags`, `linked`, `findings`, and `recommendations`. |
| `GET` | `/research/[id]` | Fetch one Research item after org-scope validation. |
| `PATCH` | `/research/[id]` | Update title, kind, status, visibility, summary, notes, tags, links, findings, or recommendations. |
| `DELETE` | `/research/[id]` | Archive a Research item by setting `status: archived` and `deleted: true`. |
| `GET` | `/research/[id]/sources` | List non-deleted sources attached to a Research item. |
| `POST` | `/research/[id]/sources` | Add a source. Requires `title`; accepts source type, URL, excerpt, media, date, publisher, confidence, verification flag, raw text, and metadata. |
| `PATCH` | `/research/[id]/sources/[sourceId]` | Update a source. |
| `DELETE` | `/research/[id]/sources/[sourceId]` | Archive a source by setting `deleted: true`. |
| `POST` | `/research/[id]/create-document` | Create or refresh a `research_report` client document from the Research item and sources. |
| `POST` | `/research/[id]/export-obsidian` | Export rendered Research and sources into the client knowledge base. |
| `GET` | `/portal/research` | Portal list of `client_visible` Research items for the active org. |
| `GET` | `/portal/research/[id]` | Portal detail view with item and sources when visible to the active org. |
| `GET` | `/portal/research/[id]/comments` | Portal comments for a visible Research item. |
| `POST` | `/portal/research/[id]/comments` | Portal comment with optional anchor and context refs. |

## Data Model

Research item fields:
- `orgId`: tenant owner.
- `title`, `slug`, `summary`, `notesMarkdown`, `tags`.
- `kind`: `competitor`, `market`, `seo`, `audience`, `content`, `ads`, `crm`, `prospect`, `brand`, `product`, `local`, `onboarding`, `internal`, or `other`.
- `status`: `draft`, `in_review`, `verified`, `used_in_document`, or `archived`.
- `visibility`: `internal` or `client_visible`.
- `linked`: `{ projectId, campaignId, seoSprintId, dealId, companyId, contactId, documentIds }`.
- `findings`: each finding has `id`, `title`, `body`, `confidence`, `status`, `sourceIds`, and `tags`.
- `recommendations`: each recommendation has `id`, `title`, `body`, `priority`, `status`, and `sourceIds`.
- `obsidian`: export state with `path`, `sourcesPath`, `exportedAt`, and `exportedBy`.

Research source fields:
- `type`: `url`, `file`, `screenshot`, `quote`, `dataset`, `email`, or `note`.
- `title`, `url`, `excerpt`, `mediaUrl`, `sourceDate`, `publisher`, `confidence`, `verified`, `rawText`, and `metadata`.

## Workflow

1. Create the Research item first, using a concrete title and the best `kind`.
2. Link it immediately with `linked.projectId`, `linked.campaignId`, `linked.seoSprintId`, `linked.dealId`, `linked.companyId`, or `linked.contactId` when context exists.
3. Add sources before final recommendations. Use `sourceIds` on findings and recommendations so evidence is traceable.
4. Keep `visibility: internal` while the item is incomplete or speculative.
5. Move to `status: verified` only when sources and confidence are good enough for decisions.
6. Use `visibility: client_visible` only for material that is safe for the client to inspect in `/portal/research`.
7. Use `/research/[id]/create-document` when the research needs polished client review, approval, signatures, or task generation.
8. Use `/research/[id]/export-obsidian` when the finding is reusable and should live in the client knowledge base. The export writes `research/<slug>.md` and `research/<slug>-sources.md`.

## Guardrails

- Research decides what is true; specs and tasks decide what to build. Do not skip straight to implementation when the facts are still unsettled.
- Do not mark a Research item `client_visible` until confidential notes, raw assumptions, and internal-only source text are removed.
- Do not use `research_report` documents as scratchpads. Keep scratch work in `research_items`; convert to documents only for reviewable output.
- Do not delete evidence to hide uncertainty. Archive stale sources and mark findings `disputed` or `outdated` when needed.
- The list route intentionally queries by org and filters in memory to avoid Firestore composite-index blockers. Preserve that pattern unless indexes are explicitly added.
- Portal users can comment on visible Research items, but admin agents remain responsible for source quality, status changes, and exports.
