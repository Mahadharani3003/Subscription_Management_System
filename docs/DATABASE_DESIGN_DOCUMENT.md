# Brightloop – Database Design & Entity-Relationship Specification
## Schema Architecture, Relational Mappings, Constraints, and Indexing Strategy
**Odoo Kochi Hackathon 2026**

---

### Table of Contents
1. [Entity-Relationship Diagram](#1-entity-relationship-diagram)
2. [Data Dictionary & Field Specifications](#2-data-dictionary--field-specifications)
3. [Relational Integrity & Foreign Key Actions](#3-relational-integrity--foreign-key-actions)
4. [Constraint Matrix (SQL & Business Validation)](#4-constraint-matrix-sql--business-validation)
5. [Indexing & Query Optimization Strategy](#5-indexing--query-optimization-strategy)

---

### 1. Entity-Relationship Diagram

```mermaid
erDiagram
    RES_COMPANY ||--o{ BRIGHTLOOP_PLAN : operates
    RES_COMPANY ||--o{ BRIGHTLOOP_SUBSCRIPTION : operates
    PRODUCT_PRODUCT ||--o{ BRIGHTLOOP_PLAN : "service sku"
    RES_PARTNER ||--o{ BRIGHTLOOP_SUBSCRIPTION : subscribes
    BRIGHTLOOP_PLAN ||--o{ BRIGHTLOOP_SUBSCRIPTION : classifies
    BRIGHTLOOP_SUBSCRIPTION ||--o{ BRIGHTLOOP_SUBSCRIPTION_LINE : contains
    BRIGHTLOOP_SUBSCRIPTION ||--o{ ACCOUNT_MOVE : generates
    BRIGHTLOOP_CHURN_REASON ||--o{ BRIGHTLOOP_SUBSCRIPTION : categorizes
    RES_USERS ||--o{ BRIGHTLOOP_SUBSCRIPTION : manages

    BRIGHTLOOP_PLAN {
        int id PK
        varchar code UK "Indexed, Unique per Company"
        varchar name "Translated Plan Name"
        int product_id FK "Service Product"
        varchar billing_interval "day, month, year"
        int billing_interval_count "Cadence multiplier"
        numeric price "Base Recurring Rate"
        int trial_period_days "Complimentary trial days"
        int grace_period_days "Dunning grace days"
        boolean auto_close_unpaid "Auto-terminate on grace breach"
        boolean active "Soft delete / archival"
        int company_id FK
    }

    BRIGHTLOOP_SUBSCRIPTION {
        int id PK
        varchar name UK "Sequential: SUB/%(year)s/00001"
        int partner_id FK "Customer (res.partner)"
        int plan_id FK "Subscription Tier"
        varchar state "draft, trial, active, paused, past_due, cancelled, closed"
        date start_date "Contract commencement"
        date trial_end_date "Trial conclusion"
        date next_billing_date "Next billing invoice target"
        date last_invoiced_date "Idempotent run protection"
        date end_date "Fixed term or cancellation date"
        date paused_date "Hiatus commencement date"
        boolean auto_renew "Auto-renewal toggle"
        numeric recurring_total "Base + Lines sum"
        numeric mrr "Normalized Monthly Recurring Revenue"
        numeric arr "Normalized Annual Recurring Revenue"
        int health_score "Predictive composite (0-100)"
        varchar churn_risk_level "low, medium, high"
        float renewal_probability "Statistical likelihood (10-99%)"
        text churn_risk_factors "Explainable diagnostic summary"
        int churn_reason_id FK "Exit code"
        text cancellation_notes "Customer offboarding feedback"
        int user_id FK "Account Manager"
        int company_id FK
    }

    BRIGHTLOOP_SUBSCRIPTION_LINE {
        int id PK
        int subscription_id FK "Parent Subscription"
        int product_id FK "Add-on / Seat Product"
        varchar name "Line item description"
        float quantity "Seat count or quota"
        numeric unit_price "Price per seat"
        numeric subtotal "quantity * unit_price"
    }

    BRIGHTLOOP_CHURN_REASON {
        int id PK
        varchar name "Reason Title"
        varchar code UK "Alphanumeric Code"
        int sequence "Display Ordering"
        boolean active "Archival toggle"
    }
```

---

### 2. Data Dictionary & Field Specifications

#### A. Table: `brightloop_plan`
- **Primary Key**: `id` (`integer`, auto-increment sequence).
- **Unique Constraint**: `unique(code, company_id)`.
- **Foreign Keys**:
  - `product_id` $\rightarrow$ `product_product.id` (`ON DELETE RESTRICT`).
  - `company_id` $\rightarrow$ `res_company.id` (`ON DELETE CASCADE`).
- **Indexed Columns**: `code`, `product_id`, `company_id`.

#### B. Table: `brightloop_subscription`
- **Primary Key**: `id` (`integer`, auto-increment sequence).
- **Unique Constraint**: `unique(name, company_id)`.
- **Foreign Keys**:
  - `partner_id` $\rightarrow$ `res_partner.id` (`ON DELETE RESTRICT`).
  - `plan_id` $\rightarrow$ `brightloop_plan.id` (`ON DELETE RESTRICT`).
  - `churn_reason_id` $\rightarrow$ `brightloop_churn_reason.id` (`ON DELETE SET NULL`).
  - `user_id` $\rightarrow$ `res_users.id` (`ON DELETE SET NULL`).
  - `company_id` $\rightarrow$ `res_company.id` (`ON DELETE CASCADE`).
- **Indexed Columns**: `name`, `partner_id`, `plan_id`, `state`, `start_date`, `next_billing_date`, `last_invoiced_date`, `end_date`, `auto_renew`, `churn_risk_level`, `user_id`, `company_id`.

#### C. Table: `brightloop_subscription_line`
- **Primary Key**: `id` (`integer`, auto-increment sequence).
- **Foreign Keys**:
  - `subscription_id` $\rightarrow$ `brightloop_subscription.id` (`ON DELETE CASCADE`).
  - `product_id` $\rightarrow$ `product_product.id` (`ON DELETE RESTRICT`).
- **Indexed Columns**: `subscription_id`, `product_id`.

#### D. Table: `brightloop_churn_reason`
- **Primary Key**: `id` (`integer`, auto-increment sequence).
- **Unique Constraint**: `unique(code)`.
- **Indexed Columns**: `code`, `sequence`.

---

### 3. Relational Integrity & Foreign Key Actions

| Parent Entity | Child Entity | Relationship | Odoo ORM Field | Foreign Key Delete Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `brightloop.subscription` | `brightloop.subscription.line` | 1-to-Many | `line_ids` | **CASCADE** (Deleting subscription cleans up its add-on lines). |
| `brightloop.subscription` | `account.move` | 1-to-Many | `invoice_ids` | **SET NULL** (Invoices must remain intact for tax/audit compliance). |
| `brightloop.plan` | `brightloop.subscription` | 1-to-Many | `subscription_ids` | **RESTRICT** (Cannot delete a plan tier with active subscribers). |
| `res.partner` | `brightloop.subscription` | 1-to-Many | `subscription_ids` | **RESTRICT** (Cannot delete a customer with subscription history). |
| `brightloop.churn.reason` | `brightloop.subscription` | Many-to-1 | `churn_reason_id` | **SET NULL** (Archiving a churn code preserves cancellation history). |

---

### 4. Constraint Matrix (SQL & Business Validation)

| Target Model | Constraint Type | Constraint Definition | Purpose |
| :--- | :--- | :--- | :--- |
| `brightloop.plan` | SQL Unique | `unique(code, company_id)` | Prevents duplicate tier codes within the same operating entity. |
| `brightloop.plan` | SQL Check | `CHECK(price >= 0)` | Disallows negative plan prices. |
| `brightloop.plan` | SQL Check | `CHECK(billing_interval_count > 0)` | Ensures billing cadence is at least 1 day/month/year. |
| `brightloop.plan` | SQL Check | `CHECK(trial_period_days >= 0)` | Disallows negative trial days. |
| `brightloop.plan` | SQL Check | `CHECK(grace_period_days >= 0)` | Disallows negative grace periods. |
| `brightloop.subscription` | SQL Unique | `unique(name, company_id)` | Guarantees reference sequence uniqueness (`SUB/%(year)s/00001`). |
| `brightloop.subscription` | Python `@api.constrains` | `_check_dates_consistency()` | Ensures `end_date >= start_date` if termination date is set. |
| `brightloop.subscription` | Python `unlink()` | `_check_unlink_state()` | Blocks deletion of contracts in `active`, `trial`, `paused`, or `past_due`. |
| `brightloop.churn.reason` | SQL Unique | `unique(code)` | Enforces unique alphanumeric reason identifiers. |

---

### 5. Indexing & Query Optimization Strategy

#### Targeted Query Use-Cases:
1. **Daily Billing Cron**:
   - Query: `WHERE state = 'active' AND next_billing_date <= CURRENT_DATE`
   - Indexes: Combined B-Tree indexes on `state` and `next_billing_date`.
2. **Dunning & Grace Period Monitor**:
   - Query: `WHERE state IN ('active', 'past_due')`
   - Optimization: Pre-filtered to subscriptions with posted unpaid invoices.
3. **Predictive Churn Watchlist**:
   - Query: `WHERE state = 'active' AND churn_risk_level IN ('high', 'medium') ORDER BY health_score ASC`
   - Indexes: Indexed `state`, `churn_risk_level`, and `health_score`.
4. **Customer Portal Dashboard**:
   - Query: `WHERE partner_id IN (CHILD_OF partner_id)`
   - Indexes: Indexed foreign key `partner_id`.
