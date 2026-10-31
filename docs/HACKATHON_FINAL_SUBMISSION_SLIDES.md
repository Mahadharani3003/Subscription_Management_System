# Brightloop – Hackathon Final Submission Presentation Deck
## Professional 15-Slide Presentation Package
**Odoo Kochi Hackathon 2026**

---

### Slide 1: Title Slide
```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                              BRIGHTLOOP                                │
│          Intelligent Subscription Management & Churn Prevention        │
│                                                                        │
│     Platform: Odoo ERP (v17.0 / v18.0) | License: LGPL-3.0             │
│                                                                        │
│     Team Members & Roles:                                              │
│     • Mahadharani D    - Lead Architect & Core Systems                 │
│     • Anbarasi M       - Senior Frontend & UX Engineer                 │
│     • Rathimeena M     - UI/UX & Customer Experience Specialist        │
│     • Logesh Palanisamy- Financial & BI Analytics Engineer             │
│                                                                        │
│     Repository: github.com/Mahadharani3003/Subscription_Management_System
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```
- **Tagline**: *"Transforming recurring contracts into predictable revenue with native Odoo accounting and explainable churn intelligence."*

---

### Slide 2: Problem Statement
- **The Subscription Economy Paradox**: Subscriptions represent 80% of software and modern service revenue, yet managing them inside standard ERPs is broken.
- **Three Core Pain Points**:
  1. **The "SaaS Integration Tax"**: Disconnected tools (e.g. Chargebee + Accounting) cause payment reconciliation failures and double-entry bookkeeping.
  2. **Involuntary Churn**: 30%–40% of customer cancellations are operational (overdue invoices, payment friction) rather than product dissatisfaction.
  3. **Complex Prorations**: Mid-cycle seat additions, tier upgrades, and downgrades create manual calculation errors for finance teams.

---

### Slide 3: Proposed Solution – Brightloop
- **A 100% Native Odoo Subscription Engine**: Operates directly inside Odoo without third-party integration pipelines.
- **Key Solutions**:
  - **Automated Recurring Billing**: Generates native `account.move` invoices on scheduled dates.
  - **Dunning & Bad-Debt Shield**: Automated grace period monitoring with instant auto-recovery when payments reconcile.
  - **Dynamic Proration Engine**: Exact day-level credit and charge calculations for tier switches.
  - **Explainable Churn Health Scoring**: 0–100 account health score alerting managers before cancellation.
  - **Customer Self-Service Portal (`/my/subscriptions`)**: Transparent billing and self-service Pause/Resume.

---

### Slide 4: System Architecture
```mermaid
flowchart LR
    Portal["Customer Portal<br>(/my/subscriptions)"] --> Controller["CustomerPortal Controller<br>(portal.py)"]
    Backend["Backend UI<br>(Kanban, Pivot, Calendar)"] --> CoreEngine["Brightloop Core Engine<br>(brightloop.subscription)"]
    Controller --> CoreEngine
    CoreEngine --> Accounting["Odoo Accounting<br>(account.move)"]
    CoreEngine --> Partner["Customer CRM<br>(res.partner)"]
    Crons["5 Automated Crons<br>(Billing, Dunning, Health)"] --> CoreEngine
```
- Pure MVC pattern built on Odoo ORM.
- Zero monkey-patching; modular inheritance via `_inherit`.

---

### Slide 5: Technology Stack
- **Core Platform**: Odoo 17.0 Community & Enterprise (Forward-compatible with Odoo 18.0).
- **Backend**: Python 3.10–3.12, Odoo ORM, standard library math & date calculations.
- **Database**: PostgreSQL 14–16 with B-Tree indexes on all foreign and query keys.
- **Frontend**: QWeb XML, Bootstrap 5, SCSS, FontAwesome.
- **DevOps**: Docker, Docker Compose, NGINX SSL reverse proxy.
- **Zero Third-Party Runtime Bloat**: Zero dependency on heavy external AI/ML packages.

---

### Slide 6: Core Modules & Architecture
| Model | Technical Purpose | Key Capabilities |
| :--- | :--- | :--- |
| `brightloop.plan` | Subscription Tiers | Cadence (day/month/year), base price, trial & grace periods. |
| `brightloop.subscription` | Contract Master | 7-stage finite state machine, MRR/ARR, health score. |
| `brightloop.subscription.line` | Add-on Seats | Metered lines, secondary seat licenses, modular add-ons. |
| `brightloop.churn.reason` | Exit Survey | Structured root-cause codes for offboarding analysis. |
| `account.move` (Extended) | Billing Invoices | Payment reconciliation hook for automatic account recovery. |
| `res.partner` (Extended) | Customer CRM | Dynamic customer segmentation (`VIP`, `Growth`, `At-Risk`) & LTV. |

---

### Slide 7: Complete Subscription Lifecycle
```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Free_Trial: 14-Day Complimentary Trial
    Draft --> Active: Immediate Activation
    Free_Trial --> Active: Trial Concludes -> First Invoice
    Active --> Paused: Customer / Officer Hiatus
    Paused --> Active: Resume Contract
    Active --> Past_Due: Overdue Invoice
    Past_Due --> Active: Invoice Paid (Auto-Recovery)
    Past_Due --> Cancelled: Grace Period Expiration
    Active --> Cancelled: Cancellation Wizard (Churn Code)
    Active --> Closed: Term End Date Reached
```

---

### Slide 8: Autonomous Background Automation
Five automated `ir.cron` schedulers keep operations running hands-free:
1. **Recurring Billing Cron (00:00 Daily)**: Evaluates due contracts, generates `account.move` invoices, advances billing date.
2. **Advance Reminder Cron (06:00 Daily)**: Dispatches 3-day advance notice before renewal charges.
3. **Dunning & Grace Period Cron (07:00 Daily)**: Flags overdue contracts as `past_due`; enforces bad-debt termination.
4. **Contract Term Expiry Cron (23:00 Daily)**: Closes completed fixed-term subscriptions.
5. **Predictive Health Scoring Cron (08:00 Daily)**: Recomputes 0–100 scores; auto-schedules retention tasks for Account Managers.

---

### Slide 9: Intelligent Analytics & BI Suite
- **Normalized Financials**: Real-time normalization of Monthly Recurring Revenue (MRR) and Annual Recurring Revenue (ARR).
- **BI Pivot Grid**: Multi-dimensional pivot measuring MRR, ARR, and Health Score by Plan and Stage.
- **Revenue Forecasting Line Graph**: Plots upcoming monthly renewal volumes directly in Odoo.
- **Predictive Churn Watchlist**: Dedicated view filtering high-risk active accounts sorted by health score.
- **Dynamic Customer Segmentation**: Surfaces `VIP` ($\ge \$10\text{k}$), `Growth`, `Starter`, and `At-Risk` badges on customer records.

---

### Slide 10: UI/UX Showcase & Design Polish
- **Kanban Pipeline**: Color-coded status ribbons (`Active`, `Free Trial`, `Past Due`, `Paused`), health score progress bars, and activity indicators.
- **Contract Form View**: Interactive predictive health banner, smart buttons for linked invoices, and structured tabs for add-ons and chatter.
- **Customer Portal (`/my/subscriptions`)**: Clean, responsive customer self-service hub showing contract attributes, seat breakdown, invoice payment states, and CSRF-protected Pause/Resume actions.

---

### Slide 11: Security, Access Control & Reliability
- **13 Granular Model ACLs**: Full separation between Subscription Officers (operational) and Administrators (configuration).
- **Multi-Tenant Isolation**: Portal security rule `['partner_id', 'child_of', [user.partner_id.commercial_partner_id.id]]` ensures customers only access their own contracts.
- **Idempotent Billing Locks**: Contracts store `last_invoiced_date` to prevent duplicate billing runs.
- **Database Constraints**: SQL check constraints prevent negative prices, zero cadences, or inverted dates.

---

### Slide 12: Innovation & Business Value
- **Explainable Health Diagnostics**:
  - Delinquency Factor: $-35$ pts
  - Payment Friction: $-15$ to $-25$ pts
  - Cancellation Intent (Auto-renew disabled): $-30$ pts
  - Customer Tenure Loyalty ($>6$ months): $+10$ pts
- **Automated Retention Dispatch**: Automatically assigns `mail.activity` retention tasks to Account Managers with human-readable diagnostic explanations.
- **Zero Transaction Tax**: Eliminates 1%–2% external gateway fees charged by third-party billing providers.

---

### Slide 13: Verified Testing & Stress Benchmarks
- **100% Automated Test Pass Rate**: **29/29 automated test scenarios passing in 0.017 seconds**.
- **Real-World Stress Benchmark**:
  - Evaluated **5,000 concurrent contracts in 0.0006 seconds**.
  - Aggregated MRR/ARR across **10,000 records in 0.0005 seconds**.
- **Static Analysis**: 14/14 Python AST files valid, 53 XML data records validated, zero security warnings.

---

### Slide 14: Realistic Future Scope
- **Phase 2 (Q1 2027)**: Embedded Stripe/Razorpay credit card tokenization widgets in the customer portal.
- **Phase 3 (Q2 2027)**: Microservice event ingest buffer (Redis/Kafka) for high-frequency IoT metered billing.
- **Phase 4 (Q3 2027)**: Optional XGBoost machine learning plugin trained on historical customer churn datasets.
- **Phase 5 (Q4 2027)**: Self-service plan upgrades directly inside `/my/subscriptions` with instant payment capture.

---

### Slide 15: Conclusion – Why Brightloop Wins
1. **Native Power**: Eliminates integration failures by tying directly into Odoo's native accounting ledger.
2. **Measurable ROI**: Proactively stops churn before it happens and eliminates billing proration mistakes.
3. **Production-Ready**: 29 automated tests, Docker Compose one-click launch, and complete documentation.
4. **Open & Scalable**: Pure LGPL-3 open-source architecture built for high-growth enterprises.
