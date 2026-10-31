# Brightloop – Production Maintenance, Operations & Support Manual
## Application Health Monitoring, Data Integrity Auditing, Disaster Recovery, and Release Management
**Odoo Kochi Hackathon 2026**

---

### Table of Contents
1. [Application Health & Systems Monitoring](#1-application-health--systems-monitoring)
2. [Data Integrity Auditing & Anomaly Detection](#2-data-integrity-auditing--anomaly-detection)
3. [Backup, Archival & Disaster Recovery Strategy](#3-backup-archival--disaster-recovery-strategy)
4. [Standard Operating Procedure: Bug Triage & Hotfix Lifecycle](#4-standard-operating-procedure-bug-triage--hotfix-lifecycle)
5. [Prioritized Product Roadmap (High, Medium, Long-Term)](#5-prioritized-product-roadmap-high-medium-long-term)
6. [Release Management & Semantic Versioning Procedure](#6-release-management--semantic-versioning-procedure)
7. [Continuous Quality Assurance (CI/CD) Guidelines](#7-continuous-quality-assurance-cicd-guidelines)
8. [Known Issues Register & Operational Troubleshooting Runbooks](#8-known-issues-register--operational-troubleshooting-runbooks)

---

### 1. Application Health & Systems Monitoring

#### A. Process Availability & Port Liveness
Brightloop relies on standard systemd service processes or container orchestrators:
```bash
# Verify systemd service status
sudo systemctl status odoo

# Verify port bindings (8069 HTTP / 8072 Longpolling / 5432 PostgreSQL)
sudo netstat -tlpn | grep -E "8069|8072|5432"
```

#### B. Server Logging & Diagnostic Filters
The production configuration (`config/odoo.conf.example`) directs logs to `/var/log/odoo/brightloop.log`. Key monitoring filter patterns:
```bash
# 1. Real-time billing cron execution monitoring:
tail -f /var/log/odoo/brightloop.log | grep -E "ir_cron_brightloop|_cron_"

# 2. Track failed transactions or ORM exceptions:
grep -E "ERROR|CRITICAL|Traceback|ValidationError" /var/log/odoo/brightloop.log | tail -n 50

# 3. Detect duplicate billing attempt warnings:
grep "already been generated" /var/log/odoo/brightloop.log
```

#### C. PostgreSQL Health & Connection Pools
Monitor database connection pool utilization and lock contention:
```sql
-- Check active connections vs max_connections:
SELECT count(*), state FROM pg_stat_activity WHERE datname = 'brightloop_prod' GROUP BY state;

-- Detect blocked queries and lock contention:
SELECT blocked_locks.pid     AS blocked_pid,
       blocking_locks.pid    AS blocking_pid,
       blocked_activity.query AS blocked_statement
FROM  pg_catalog.pg_locks         blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks         blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
   AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
   AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
WHERE NOT blocked_locks.GRANTED;
```

#### D. Automated Cron Liveness Auditing
To audit whether background schedulers are executing on schedule, query `ir_cron`:
```sql
SELECT id, cron_name, nextcall, numbercall, active 
FROM ir_cron 
WHERE cron_name LIKE 'Brightloop%' AND active = TRUE;
```

---

### 2. Data Integrity Auditing & Anomaly Detection

To ensure transactional consistency across contracts, invoices, and accounting journals, execute our standalone automated diagnostic utility:
```bash
python scripts/health_check_and_audit.py
```

#### SQL Data Integrity Audit Queries for Support Engineers:

```sql
-- 1. Identify active contracts that are due for billing but have not been invoiced:
SELECT s.id, s.name, s.partner_id, s.next_billing_date, s.last_invoiced_date 
FROM brightloop_subscription s
WHERE s.state = 'active' 
  AND s.next_billing_date <= CURRENT_DATE 
  AND (s.last_invoiced_date IS NULL OR s.last_invoiced_date < s.next_billing_date);

-- 2. Detect delinquent contracts where grace period has expired without status shift:
SELECT s.id, s.name, s.state, p.grace_period_days, m.invoice_date_due
FROM brightloop_subscription s
JOIN brightloop_plan p ON p.id = s.plan_id
JOIN account_move m ON m.subscription_id = s.id
WHERE s.state IN ('active', 'past_due')
  AND m.state = 'posted' 
  AND m.payment_state IN ('not_paid', 'partial')
  AND m.invoice_date_due < (CURRENT_DATE - INTERVAL '1 day' * p.grace_period_days);

-- 3. Detect orphaned subscription lines:
SELECT l.id, l.name, l.subscription_id 
FROM brightloop_subscription_line l
LEFT JOIN brightloop_subscription s ON s.id = l.subscription_id
WHERE s.id IS NULL;
```

---

### 3. Backup, Archival & Disaster Recovery Strategy

#### Backup Topology:
- **Daily Full Backup**: Automated script [`scripts/backup_brightloop.sh`](file:///C:/Users/mahad/.gemini/antigravity-ide/scratch/brightloop/scripts/backup_brightloop.sh) executed at 02:00 UTC via system cron.
- **Retention**: 30 rolling daily snapshots on disk; monthly snapshots archived to cold offsite S3/GCS bucket.
- **Data Encapsulation**: PostgreSQL binary dump (`pg_dump -Fc`) + Odoo filestore tarball + SHA-256 verification manifest.

#### Disaster Recovery Runbook:
To recover a corrupted or destroyed instance onto a clean database in under 5 minutes:
```bash
# Run the automated restoration script:
./scripts/restore_brightloop.sh /var/backups/brightloop/brightloop_prod_20261031.dump brightloop_prod /var/backups/brightloop/filestore_brightloop_prod_20261031.tar.gz

# Execute schema synchronization:
odoo-bin -c /etc/odoo/odoo.conf -d brightloop_prod -u brightloop_subscription --stop-after-init
```

---

### 4. Standard Operating Procedure: Bug Triage & Hotfix Lifecycle

Every reported issue must follow this 6-step triage pipeline:

```
[Issue Reported] ──► 1. Reproduce in Test Sandbox
                         │
                         ▼
                     2. Root Cause Analysis (Model / View / Cron)
                         │
                         ▼
                     3. Smallest Reliable Fix (Zero Side-Effects)
                         │
                         ▼
                     4. Add Regression Test in tests/
                         │
                         ▼
                     5. Run verify_backend.py & Full Test Suite (29 tests)
                         │
                         ▼
                     6. Document Resolution in Changelog & Deploy Hotfix
```

#### Triage Priority Matrix:
- **P0 - Blocker (SLA: 2 hours)**: Duplicate billing, data loss, cron crashes, payment recovery failure.
- **P1 - Critical (SLA: 8 hours)**: Inaccurate proration calculation, portal access failure, health score miscalibration.
- **P2 - Moderate (SLA: 48 hours)**: Visual alignment flaw in Kanban cards, email template typo, non-critical filter issue.
- **P3 - Low (SLA: Next Release)**: Feature requests, minor styling improvements.

---

### 5. Prioritized Product Roadmap (High, Medium, Long-Term)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        BRIGHTLOOP PRODUCT ROADMAP                                │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  [HIGH PRIORITY - Q1 2027]                                                       │
│  • Stripe / Razorpay Native Portal Card Elements (Direct customer checkout)     │
│  • Customer Self-Service Plan Upgrades in /my/subscriptions                     │
│  • Multi-Currency Real-time Hedging & Automated Revaluation                      │
│                                                                                  │
│  [MEDIUM PRIORITY - Q2 2027]                                                     │
│  • Consolidated Multi-Entity Billing Statements (Parent-child accounts)          │
│  • High-Frequency Event Ingest Buffer (Redis / ClickHouse connector)            │
│  • Contract Renewal Quote Generation (CPQ integration)                           │
│                                                                                  │
│  [LONG-TERM OPPORTUNITIES - Q3-Q4 2027]                                          │
│  • XGBoost / LightGBM Machine Learning Churn Predictor Sidecar                   │
│  • Dynamic Pricing Optimization & Usage Tier Elasticity Modeling                 │
│  • Mobile App Portal (Flutter / React Native integration)                        │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

### 6. Release Management & Semantic Versioning Procedure

Brightloop follows Odoo Semantic Versioning: `17.0.X.Y.Z`
- `17.0`: Core Odoo platform target version.
- `X`: Major architectural release (breaking changes / major models).
- `Y`: Minor feature addition (new views, wizards, non-breaking fields).
- `Z`: Patch / Hotfix release (bug fixes, performance optimizations).

#### Release Checklist:
1. Bump version in [`brightloop_subscription/__manifest__.py`](file:///C:/Users/mahad/.gemini/antigravity-ide/scratch/brightloop/brightloop_subscription/__manifest__.py).
2. Execute full verification suite:
   ```bash
   python verify_backend.py
   python -m unittest discover -s tests -p "test_*.py"
   python scripts/health_check_and_audit.py
   ```
3. Update `CHANGELOG.md` with release notes and author credits.
4. Tag commit in git: `git tag -a v17.0.1.0.0 -m "Release 17.0.1.0.0"`
5. Deploy to staging, verify upgrade with `-u brightloop_subscription`, then promote to production.

---

### 7. Continuous Quality Assurance (CI/CD) Guidelines

Our automated CI pipeline validates three distinct test suites:

| Suite Name | Script Path | Scenarios Evaluated | Pass Criteria |
| :--- | :--- | :--- | :--- |
| **Static & XML Verification** | `verify_backend.py` | AST parsing, 21 views/templates, 14 actions, 13 ACL rules. | 100% Valid XML/AST |
| **Lifecycle Workflows** | `tests/test_subscription_workflows.py` | 10 lifecycle transitions (trial, upgrade, dunning, cancellation). | Zero Exceptions |
| **System Integration & QA** | `tests/test_full_system_integration.py` | 9 integration tests (proration, security, portal, reporting). | Zero Exceptions |
| **Stress & Edge Cases** | `tests/test_stress_and_edge_cases.py` | 10 real-world scenarios, 5,000 contract batch load, constraints. | $<250\text{ms}$ Execution |
| **Operational Health** | `scripts/health_check_and_audit.py` | 5 operational integrity diagnostics. | Exit Code 0 |

---

### 8. Known Issues Register & Operational Troubleshooting Runbooks

#### Runbook 1: Contract Shows "Past Due" After Customer Paid Invoice
- **Root Cause**: Invoice was reconciled against a bank statement manually without triggering `action_post()` or `payment_state` recomputation.
- **Resolution**:
  1. Open the invoice in Odoo Invoicing.
  2. Verify that `payment_state` reads `paid` or `in_payment`.
  3. Click **Refresh Payment State** or open the linked subscription and click **Action Recompute Health Score**. The contract restores to `active`.

#### Runbook 2: Daily Recurring Billing Cron Did Not Generate Invoices
- **Root Cause**: The cron was paused or the scheduled time passed during server maintenance.
- **Resolution**:
  1. Navigate to **Settings $\rightarrow$ Technical $\rightarrow$ Scheduled Actions $\rightarrow$ Brightloop: Automated Daily Recurring Invoicing**.
  2. Verify `active == True`.
  3. Click **Run Manually**. The idempotent safeguard ensures only due contracts are billed, preventing double-billing.

#### Runbook 3: Portal User Cannot See Their Subscription
- **Root Cause**: The portal user's `res.partner` is not configured as a child contact of the commercial organization owning the subscription.
- **Resolution**:
  1. Open **Contacts** and locate the subscriber's parent company.
  2. Ensure the portal user contact is linked to that company.
  3. Re-login as the portal user and refresh `/my/subscriptions`.
