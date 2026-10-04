# MailPilot — Affiliate Email Marketing & Sending Engine Direction

## Purpose

This document records the agreed product direction and the next implementation priorities for MailPilot.

The goal is to evolve MailPilot into a reliable email marketing platform suitable for affiliate email marketing, while preserving the existing feature-based architecture and reusing existing components wherever possible.

This is a planning/architecture record. It is not a substitute for the actual code and should be updated when the agreed architecture changes.

---

# 1. Product Direction

MailPilot will support an affiliate email marketing workflow built around:

```text
Responders
    ↓
Affiliate Offers
    ↓
Email Templates / Ready Emails
    ↓
Campaigns
    ↓
Contacts / Audiences
    ↓
Sending Pools
    ↓
SMTP Senders
    ↓
Sending Engine
    ↓
Tracking & Analytics
```

The platform should make it possible to manage multiple responders, each with their own affiliate offers, and use those offers in reusable emails and campaigns.

A future integration with CX3 Ads is planned. CX3 should be treated as an external affiliate-offer source; the integration should be built on top of the internal affiliate/offer domain rather than making the internal model CX3-specific.

---

# 2. Immediate Priority: Reliable Email Sending

Before implementing the CX3/affiliate integration, the core email sending flow must be reliable.

The first major milestone is:

```text
Create Account
    ↓
Add SMTP Sender
    ↓
Verify / Test Sender
    ↓
Import Contacts
    ↓
Use Ready Email / Template
    ↓
Create Campaign
    ↓
Personalize Email
    ↓
Send Test
    ↓
Queue Campaign
    ↓
Sending Engine
    ↓
Distribute Across Sender Pool
    ↓
SMTP
    ↓
Track Results
```

The current sending implementation is not yet sufficient for this goal. The sending engine needs durable queueing, sender-aware capacity management, rate limiting, retries, and safe concurrency.

---

# 3. Multiple Senders & Sending Pools

A campaign must not be tied to a single SMTP sender when multiple senders are available.

MailPilot will support a **Sending Pool** concept.

A pool contains sender accounts that can be used to send campaign messages.

Example:

```text
Main Marketing Pool
├── SMTP Sender A
├── SMTP Sender B
├── SMTP Sender C
└── SMTP Sender D
```

A campaign can select a sending pool, and the sending engine decides which sender handles each queued email.

The system must account for the fact that different SMTP accounts may have different limits.

---

# 4. Per-Sender Sending Limits

Sending limits must be configurable per sender.

The design must NOT hard-code a global value such as 50 messages.

Potential sender-level controls include:

- Batch size
- Delay between messages
- Rate limit
- Hourly limit
- Daily limit
- Cooldown
- Enabled/disabled status
- Priority (if needed)

Only fields justified by the implementation should be added.

Example:

```text
Sender A
Batch: 50
Daily limit: 500

Sender B
Batch: 30
Daily limit: 300

Sender C
Batch: 20
Daily limit: 200
```

The sending engine must respect each sender's configured capacity.

---

# 5. Sending Queue

Campaign messages should enter a durable sending queue instead of being sent directly from the HTTP request.

Conceptually:

```text
Campaign
    ↓
Create Send Jobs
    ↓
QUEUED
    ↓
ASSIGNED
    ↓
SENDING
    ↓
SENT
```

Failures follow:

```text
SENDING
    ↓
FAILED
    ↓
RETRYING
    ↓
SENT
```

Possible terminal state:

```text
FAILED
```

after the retry policy is exhausted.

The exact implementation should reuse the existing `EmailDelivery` model where practical rather than creating duplicate concepts unnecessarily.

---

# 6. Concurrency & Duplicate Protection

Multiple workers must never send the same queued email twice.

The sending engine must use safe job claiming and state transitions.

The design should account for:

- Concurrent workers
- Worker crashes
- Stale jobs
- Lease/lock expiration
- Atomic state transitions
- Transaction boundaries
- Server restarts

Existing campaign-level locking should be preserved where useful, but message-level protection is required for reliable individual delivery.

---

# 7. Sender Selection & Distribution

The sending engine should distribute queued emails across available senders.

The first version should prefer a simple, predictable selection strategy rather than an unnecessarily complex algorithm.

The engine must consider:

- Sender enabled/disabled state
- Remaining capacity
- Batch capacity
- Rate limits
- Daily/hourly limits
- Cooldown
- Sender failures

Example:

```text
Sender A → capacity 50
Sender B → capacity 30
Sender C → capacity 20

Queued contacts → 100
```

A valid first distribution is:

```text
A → 50
B → 30
C → 20
```

The number 50 is only an example. Actual limits come from sender configuration.

---

# 8. Retry Strategy

The sending engine must distinguish retryable failures from permanent failures.

Retryable examples may include:

- Temporary SMTP connection failures
- Temporary provider errors
- Rate-limit responses

Permanent examples may include:

- Invalid recipient
- Permanent SMTP rejection
- Invalid sender configuration

The exact retry policy should be configurable or centrally defined, with a maximum number of attempts and an appropriate backoff strategy.

---

# 9. SMTP Provider Abstraction

The current implementation has Gmail-specific sending behavior.

The target architecture should move toward a provider abstraction so sender accounts are not hard-coded to Gmail.

For V1, generic SMTP is sufficient.

Conceptually:

```text
SenderAccount
    ↓
Email Provider
    ↓
SMTP
```

Future providers can be added without rewriting campaign logic.

SMTP credentials must never be returned through APIs or exposed in logs.

---

# 10. Contacts & Audiences

MailPilot needs a practical contact workflow.

Required direction:

- Add individual contacts
- Import contacts from CSV
- Validate imported data
- Handle duplicates
- Track unsubscribe/suppression status
- Select an audience for a campaign

The campaign should send only to eligible contacts.

---

# 11. Ready Emails & Templates

MailPilot should support reusable email content.

There are two useful concepts:

### Ready Email

A complete email that is already prepared for sending.

It may contain:

- Subject
- HTML
- Text
- CTA
- Links

### Template

Reusable email content that can contain variables.

Future personalization examples:

```text
{{first_name}}
{{offer_name}}
{{offer_description}}
{{tracking_url}}
{{offer_cta_label}}
```

The template itself should remain reusable. A campaign should render a final message from the template plus campaign/contact/offer data rather than permanently modifying the original template.

The current system can store HTML inside templates, but HTML file import and full variable rendering are not yet complete and should be treated as implementation work.

---

# 12. Affiliate Responders

A **Responder** is a first-class business concept.

There may be multiple responders, and each responder has their own offers.

Relationship:

```text
Responder
    └── Offers
```

Example:

```text
Responder A
├── Offer 1
├── Offer 2
└── Offer 3

Responder B
├── Offer 4
└── Offer 5
```

The offer should therefore not be treated as an isolated global record.

---

# 13. Affiliate Offers

The current offer model is a basic offer catalog. It needs to evolve for affiliate marketing.

The future affiliate offer should be able to represent information such as:

- External offer ID
- Name
- Payout
- Payout type
- Vertical
- GEO
- Tags
- Status
- Tracking URL
- Landing URL
- Description
- Restrictions
- Start/end dates
- Responder ownership

The exact fields should be based on real source data rather than assumptions.

---

# 13A. Offers & Responders — Product Decisions

This section refines sections 12 and 13. It records product and architecture decisions from the Offers & Responders audit. It is **not** an implementation specification. Status markers below reflect the implementation in the working tree at the time of the last update; recording a decision does not itself change schema, API, migrations or code.

Legend:

- **DECIDED** — locked product/architecture decision.
- **DECIDED FOR MVP** — locked for the MVP; may be revisited by a later explicit product decision.
- **IMPLEMENTED** — decided and implemented in code (and covered by tests); not necessarily deployed to production.
- **NOT YET IMPLEMENTED** — the behavior is decided, but the implementation details are left to the implementation phase.
- **NOT YET DECIDED / DEFERRED** — intentionally open; do not treat as a requirement.

## 13A.1 Preserve existing Offers / backward compatibility — DECIDED

- The existing Offer implementation must NOT be removed or broken.
- Existing promotion-related fields and behavior remain available for existing campaigns.
- Affiliate Offer capabilities are added **on top of** the existing system rather than replacing the existing Offer behavior immediately.

## 13A.2 Responder ownership — DECIDED

Target ownership model:

```text
User
  ↓
Responder
  ↓
Offer
  ↓
OfferVariant
```

- A User can have multiple Responders.
- Each Responder owns its own Offers.
- Offers belonging to one Responder must not accidentally become available to another Responder.

## 13A.3 Default Responder for existing Offers — DECIDED

Existing Offers that predate the Responder system must not require manual cleanup. During the eventual migration/backfill, each existing User receives a Default Responder if necessary, and their existing Offers are associated with it.

```text
User
└── Default Responder
    ├── Existing Offer 1
    ├── Existing Offer 2
    └── Existing Offer 3
```

This is a migration/backfill decision only. **IMPLEMENTED** (migration `c3d4e5f6a7b8` backfills per-user Default Responders; new Offers without a Responder get the same user's default). Not applied to production until that migration is deployed.

**Decision (locked after the Phase 2D-6 audit) — DECIDED / DECIDED FOR MVP:**

- Existing Offers with `responder_id = NULL` will eventually be assigned, during the migration/backfill, to a Default Responder belonging to the **same User**. An Offer MUST NOT be assigned to another user's Default Responder.
- The Default Responder is **user-scoped**. A global shared Default Responder MUST NOT be created.
- The existing implementation that provides a Default Responder for **new** Offers is intentional for MVP and remains unless a later product decision changes it.
- **Invariant:** for every Offer that has a Responder, `Offer.user_id == Offer.responder.user_id`.

```text
User
  ↓
Responder
  ↓
Offer
  ↓
OfferVariant
```

## 13A.4 Affiliate destination — DECIDED

An Affiliate Offer has its own `affiliate_url`, separate from the existing `cta_url`.

```text
Offer
├── existing promotion metadata
├── cta_url
└── affiliate_url
```

- The existing `cta_url` is not reinterpreted or removed.
- `affiliate_url` represents the affiliate destination of the Affiliate Offer.
- Affiliate click tracking must eventually preserve the exact original affiliate destination.
- **IMPLEMENTED:** click tracking carries the exact original destination in the signed token (`track_links` in `app/infrastructure/email/smtp.py`).

## 13A.5 Offer vs Email Creative — DECIDED

Offer identity is separate from Email Creative / Variant. An Offer must NOT be modeled as only `subject` + `html`. One Offer can contain multiple Variants.

```text
Offer
├── Variant A
├── Variant B
└── Variant C
```

## 13A.6 OfferVariant — DECIDED

Planned MVP structure:

```text
Offer
  ↓
OfferVariant
```

A Variant represents one email creative belonging to an Offer. Minimum planned fields:

```text
id
offer_id
name
content_type
from_name
subject
body_html
body_text
image_url
is_active
created_at
```

- No speculative fields are added.
- **IMPLEMENTED:** the `OfferVariant` model, migration and API exist.

## 13A.7 Variant content types — DECIDED

The MVP supports these creative types:

```text
TEXT
IMAGE
TEXT_IMAGE
HTML
```

A single Offer may contain Variants of different content types:

```text
Offer
├── Variant A → TEXT
├── Variant B → IMAGE
├── Variant C → TEXT_IMAGE
└── Variant D → HTML
```

The system must not assume every Offer is an HTML email.

## 13A.8 Image handling — DECIDED FOR MVP

For the MVP, image content is represented by an image URL (`image_url`). The following are NOT introduced unless a later product decision explicitly requires them:

- S3
- Cloudinary
- a media service
- a complex upload system
- a media-management subsystem

## 13A.9 Variant selection — DECIDED FOR MVP

For the MVP, Variant selection is **MANUAL**: the user/campaign explicitly selects the Variant to use.

Not implemented (remain future possibilities only): A/B testing, random selection, rotation, weighted selection, performance-based selection, automatic optimization.

## 13A.10 Campaign relationship — DECIDED

```text
Campaign
  ↓
Offer
  ↓
Variant
```

- The existing Campaign → Offer relationship remains.
- A Campaign will eventually be able to reference the selected Variant.

```text
Campaign
├── offer_id
└── variant_id
```

- Variant selection is manual for the MVP.
- Database/API changes: **IMPLEMENTED** (`campaigns.variant_id`, manual selection via the campaign API).

## 13A.11 Existing Campaign email content — DECIDED

- Existing Campaign email content and snapshot behavior must remain backward compatible.
- Existing Campaign fields such as subject/body/from_name must NOT be removed just because OfferVariants are introduced.
- The future Offer/Variant implementation must be introduced without breaking existing campaigns.
- No migration or restructuring is performed as part of this decision.

## 13A.12 Legacy promotion block — DECIDED (product behavior)

- Existing promotion-block behavior remains available for legacy Offers/Campaigns.
- For new Affiliate Offers using OfferVariants, the Variant represents the email creative.
- The legacy promotion block is not automatically injected into a Variant-based Affiliate email unless explicitly required.

Implementation of this separation: **IMPLEMENTED** (a campaign with a Variant does not get the legacy promotion block).

## 13A.13 Responder deletion — DECIDED

A Responder that still owns Offers must NOT be cascade-deleted. MVP behavior:

```text
Responder with Offers
→ deletion blocked
```

This avoids accidentally deleting Offers and their Variants.

**Decision (locked after the Phase 2D-6 audit) — DECIDED:** A Responder MUST NOT be deleted while it owns any Offers. Return `409 Conflict`. An empty Responder (owning no Offers) may be deleted. **IMPLEMENTED.**

## 13A.13A Deletion of referenced Offers and Variants — DECIDED

Locked after the Phase 2D-6 audit. **IMPLEMENTED** (`409 Conflict` from `OfferService`; covered by tests).

**Offer deletion.** An Offer MUST NOT be deleted if it is referenced by any Campaign.

- Return `409 Conflict`; the Campaigns remain unchanged.
- The user must first detach/change the affected Campaigns before the Offer can be deleted.

**Variant deletion.** A Variant MUST NOT be deleted if it is referenced by any Campaign.

- Return `409 Conflict`; the Campaigns remain unchanged.
- The user must first change or clear the Variant selection on the affected Campaigns before deleting the Variant.

**Responder deletion.** Unchanged (see 13A.13): blocked with `409 Conflict` while it owns any Offers.

**Forbidden behaviors** (for both Offer and Variant deletion):

- Do NOT clear `campaign.offer_id`.
- Do NOT clear `campaign.variant_id`.
- Do NOT fall back to Campaign placeholder content.
- Do NOT silently change what a Campaign will send, or change Campaign content automatically.

**Reason:** a Campaign that loses its Offer/Variant could fall back to its stored placeholder subject/body and accidentally send the wrong content.

## 13A.14 Affiliate CTA requirement — DECIDED (requirement only)

- Variants may contain affiliate CTA links.
- When click tracking is applied, the existing click-tracking system must eventually preserve the original affiliate destination (see 13A.4).
- No tracking code is changed as part of this decision.

## 13A.15 Personalization — NOT YET DECIDED / DEFERRED

- Personalization is NOT part of this implementation phase.
- Future OfferVariants may support recipient-specific fields such as `{{first_name}}`, but the syntax is not finalized, the templating engine is not finalized, and implementation is deferred.

## 13A.16 Explicitly deferred features (outside the MVP)

None of the following is to be implemented as part of the MVP:

- A/B testing
- automatic variant rotation
- random variant selection
- weighted variant selection
- performance-based variant optimization
- advanced email template builder
- drag-and-drop editor
- external media storage
- advanced personalization engine
- template version history
- template marketplace

## 13A.17 Architecture summary — planned MVP

```text
User
  │
  └── Responder
        │
        └── Offer
              │
              ├── affiliate_url
              │
              └── OfferVariant
                    ├── TEXT
                    ├── IMAGE
                    ├── TEXT_IMAGE
                    └── HTML
```

```text
Campaign
  ├── Offer
  └── selected Variant
```

This is the **planned MVP architecture**. It is documentation only; implementation will happen in a later phase.

---

# 14. CX3 Ads Integration

CX3 Ads is planned as an external offer source.

The intended future flow is:

```text
CX3 Ads
    ↓
Import / Sync
    ↓
Normalize
    ↓
Match by external Offer ID
    ↓
New / Existing / Updated
    ↓
Responder's Offer Catalog
```

The system should be able to answer:

- Which CX3 offers already exist in MailPilot?
- Which offers are new?
- Which offers changed?
- Which offers are no longer active?
- Which offers belong to which responder?

CX3-specific data should be mapped into the internal affiliate offer model rather than making the whole application depend on CX3 terminology.

---

# 15. Campaign Flow

The target campaign workflow is:

```text
Select Responder / Offer
        ↓
Select Email / Template
        ↓
Select Audience
        ↓
Select Sending Pool
        ↓
Render Personalized Email
        ↓
Send Test
        ↓
Queue Campaign
        ↓
Sending Engine
        ↓
SMTP
        ↓
Tracking / Analytics
```

The campaign should retain the relationship between:

- Sender
- Audience
- Email
- Offer
- Responder
- Delivery result

---

# 16. Analytics & Tracking

Each delivery should produce a durable result.

The system should eventually support:

- Queued
- Assigned
- Sending
- Sent
- Failed
- Retrying
- Bounced
- Unsubscribed

Campaign-level metrics should include useful counts such as:

```text
Total
Queued
Sending
Sent
Failed
Retrying
```

Existing unsubscribe and click-tracking behavior should be preserved while the sending engine is improved.

---

# 17. Implementation Priority

## P0 — Reliable Sending Foundation

1. Review and improve SenderAccount
2. Generic SMTP/provider abstraction
3. Sender-level limits
4. Sending Pool
5. Durable message queue
6. Safe job claiming/concurrency protection
7. Sender capacity calculation
8. Rate limiting / batch handling
9. Retry strategy
10. Campaign progress/state handling
11. Secure sender credentials
12. Fix existing sending/tracking issues
13. Send test flow
14. Verify real end-to-end sending

## P1 — Affiliate Email Workflow

1. Responder entity
2. Responder → Offer relationship
3. Improve affiliate Offer model
4. Ready Email / Template improvements
5. Personalization variables
6. Audience/contact improvements
7. Campaign ↔ Offer ↔ Responder flow

## P2 — CX3 & Intelligence

1. CX3 import/sync
2. External Offer ID matching
3. New/Existing/Updated detection
4. Offer synchronization history
5. Offer filtering and discovery
6. Offer recommendations / scoring
7. Advanced analytics

---

# 18. Architectural Principles

The following principles should be preserved during implementation:

- Reuse existing MailPilot components where practical.
- Do not duplicate existing domain concepts unnecessarily.
- Preserve the feature-based backend architecture.
- Keep API → Service → Repository → Model boundaries.
- Keep background work in workers rather than HTTP requests.
- Use Alembic for schema changes.
- Prefer durable database-backed state for sending jobs.
- Avoid unnecessary infrastructure for V1.
- Do not hard-code SMTP limits.
- Do not make the internal domain CX3-specific.
- Protect sender credentials.
- Prevent duplicate sends.
- Make failures recoverable.
- Keep the system observable.
- Implement incrementally and verify each phase before moving to the next.

---

# 18A. Known Technical Risk — Alembic Migration Chain

**This is a technical/deployment issue, NOT a product decision.** It is to be handled in a separate migration/deployment-hardening phase. No repair has been attempted.

- The current Alembic migration chain cannot build a fresh database from empty to head: an older migration attempts to create the already-existing `campaigns` table.
- The real `emails.db` is behind the current migration head.
- Migrations must not be run blindly against production data.
- Migration repair and backfill (including the Default Responder backfill in 13A.3) must be tested first against a copy or a temporary database.

---

# 19. Current vs Target

### Current

```text
Campaign
    ↓
Background execution
    ↓
CampaignSenderService
    ↓
Gmail SMTP
```

### Target

```text
Campaign
    ↓
Send Jobs
    ↓
Durable Queue
    ↓
Sending Manager
    ↓
Sending Pool
    ├── Sender A
    ├── Sender B
    └── Sender C
    ↓
Per-Sender Limits / Rate Control
    ↓
SMTP Provider
    ↓
Delivery Result
    ↓
Analytics
```

---

# 20. Decision Record

This document records the agreed direction as of the current planning phase.

Before implementing the next major feature, the codebase should be checked against this document and any deviations should be explicitly discussed rather than silently introduced.

The immediate implementation target is the **Reliable Multi-Sender Sending Engine**.

CX3/Responder/affiliate intelligence comes after the sending foundation is reliable.
