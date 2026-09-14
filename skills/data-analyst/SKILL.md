---
name: data-analyst
description: Analytics, attribution, dashboard, reporting, and data-quality work for Partners in Biz. Use for product analytics, funnels, retention, reporting QA, metric reconciliation, and data-backed recommendations.
---

# Data Analyst

Use this skill for analytics and reporting work that requires careful evidence,
data-quality checks, and reproducible numbers.

## Ownership

- Product analytics readouts
- Funnel and retention analysis
- Attribution and dashboard checks
- Report metric reconciliation
- Data-quality issues and anomaly investigation

## Rules

- State the query/source used for each number.
- Treat missing, stale, or inconsistent data as a blocker.
- Link final analysis to the relevant task, report, property, campaign, SEO sprint, or client document.
- For PiB product analytics, treat `properties/{propertyId}.orgId` as the source of truth for client ownership. Never analyze or report on a raw `propertyId` without verifying the property belongs to the selected client org.
- For SEO/client website reports, prefer `/portal/reports` with the selected client and property when the readout is property-specific. The report snapshot uses first-party `product_sessions` and `product_events` as fallback web KPIs for sessions, pageviews, users, and conversions when no metrics fact rows exist.
