# Brightloop – Subscription Management System
> **Odoo Kochi Hackathon 2026**  
> *A modern, enterprise-grade recurring billing, subscription lifecycle, and predictive churn management system built natively on Odoo 17.*

[![Odoo Version](https://img.shields.io/badge/Odoo-17.0%20%7C%2018.0-purple.svg)](https://www.odoo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-LGPL--3-green.svg)](LICENSE)
[![QA & Tests](https://img.shields.io/badge/Tests%20Passing-19%2F19%20(100%25)-brightgreen.svg)](#-testing--quality-assurance)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](docker-compose.yml)

---

## 🌟 Executive Overview

**Brightloop** is an end-to-end subscription management, automated billing, and churn analytics platform developed for the **Odoo Kochi Hackathon**. Built with pure Odoo architectural standards, it operates natively alongside Odoo Invoicing (`account.move`), communication threads (`mail.thread`), scheduled activities (`mail.activity`), and the customer self-service web portal (`portal`).

### Key Capabilities
- ⚡ **Multi-Cadence Plan Engine**: Configure recurring subscriptions across daily, monthly, annual, or custom cycle counts with trial periods and grace policies.
- 🔄 **Autonomous Recurring Billing**: Daily automated `ir.cron` scheduler generating compliant `account.move` customer invoices with accurate tax calculations and journal lines.
- 🛡️ **Dunning & Bad-Debt Protection**: Automated payment grace period monitoring, retry notifications, and auto-suspension upon prolonged arrears.
- ⚖️ **Proration Engine**: Immediate plan upgrades and downgrades with exact day-level credit and charge calculations.
- 🔒 **Zero Duplicate Protection**: Idempotent billing pipeline preventing duplicate invoices even on simultaneous manual or cron runs.
- 📊 **Real-time Financial Metrics**: Automatic calculation of Monthly Recurring Revenue (MRR) and Annual Recurring Revenue (ARR).
- 🧩 **Modular Add-ons & Seat Metering**: Dynamically attach per-user seats and modular features to any active contract.
- 🔮 **Predictive Churn Risk & Health Scoring**: Composite score (0–100) with diagnostic factors and automated retention task scheduling.
- 👤 **Customer Self-Service Portal (`/my/subscriptions`)**: View contract details, line items, billing history, and self-service Pause/Resume.
- 📈 **Revenue Forecasting & Churn Watchlist**: Dedicated renewal timeline graph and prioritized retention watchlist.
- 🔒 **Enterprise Role-Based Access Control**: Granular separation of duties between Subscription Officers, Administrators, and self-service Portal Customers.

---

## 🏗️ Architecture & Native Integration

```mermaid
flowchart TD
    subgraph UI_Layer [Presentation & Interaction]
        Kanban["Kanban Pipeline with Visual Statuses"]
        Forms["Smart Forms with Ribbons & Chatter"]
        Wizards["Upgrade / Downgrade & Cancellation Modals"]
        Pivot["MRR / ARR Analytics & Pivot Views"]
        Forecast["Revenue Forecasting Line Graph"]
        Portal["Customer Self-Service Portal (/my/subscriptions)"]
    end

    subgraph Business_Engine [Core Engine]
        StateMachine["Contract State Machine"]
        BillingCron["Daily Recurring Invoicing Cron"]
        Dunning["Dunning & Grace Period Engine"]
        Proration["Prorated Plan Switch Engine"]
        MRR["Normalized MRR / ARR Engine"]
        HealthScore["Predictive Churn Health Scoring"]
    end

    subgraph Native_Odoo [Odoo Native Integration]
        Plan["brightloop.plan"]
        Sub["brightloop.subscription"]
        Lines["brightloop.subscription.line"]
        Partner["res.partner <Extended with LTV & Segments>"]
        AccountMove["account.move <Native Invoices & Auto-Recovery>"]
    end

    UI_Layer --> Business_Engine
    Business_Engine --> Native_Odoo
    BillingCron -->|Generates Invoices| AccountMove
    AccountMove -->|Payment Reconciliation Hook| StateMachine
```

---

## 📂 Repository Structure

```
.
├── brightloop_subscription/                 # Core Odoo Custom Addon Module
│   ├── __init__.py                          # Addon init loader
│   ├── __manifest__.py                      # Module metadata & dependencies
│   ├── controllers/
│   │   ├── __init__.py                      # Controller loader
│   │   └── portal.py                        # /my/subscriptions portal routes & actions
│   ├── models/
│   │   ├── brightloop_plan.py               # Subscription tier & pricing rules
│   │   ├── brightloop_churn_reason.py       # Cancellation root-cause categorization
│   │   ├── brightloop_subscription.py       # Primary contract, lifecycle & health scoring
│   │   ├── brightloop_subscription_line.py  # Add-ons & seat metering lines
│   │   ├── account_move.py                  # Native invoice extension & payment recovery hook
│   │   └── res_partner.py                   # Customer profile links, LTV & segmentation
│   ├── wizards/
│   │   ├── brightloop_change_plan_wizard.py # Prorated upgrade/downgrade wizard
│   │   └── brightloop_cancel_wizard.py      # Churn categorization offboarding wizard
│   ├── security/
│   │   ├── brightloop_security.xml          # User & Manager Groups + Record Rules
│   │   └── ir.model.access.csv              # Granular CRUD ACL permissions (13 rules)
│   ├── data/
│   │   ├── ir_sequence_data.xml             # Auto-sequence (SUB/%(year)s/00001)
│   │   ├── ir_cron_data.xml                 # 5 automated crons (billing, dunning, health)
│   │   └── mail_template_data.xml           # 8 automated email templates
│   ├── views/
│   │   ├── brightloop_wizard_views.xml      # Upgrade & Cancel modal views
│   │   ├── brightloop_plan_views.xml        # Plan kanban, tree, and form views
│   │   ├── brightloop_subscription_views.xml# Kanban, form, tree, calendar, pivot, graphs
│   │   ├── brightloop_churn_reason_views.xml# Churn configuration views
│   │   ├── res_partner_views.xml            # Customer smart button, LTV badge & tab
│   │   ├── brightloop_subscription_portal_templates.xml # Customer portal QWeb templates
│   │   └── brightloop_menus.xml             # 17 menuitems and 14 window actions
│   ├── static/
│   │   ├── description/icon.png             # Module branding icon (128x128)
│   │   └── src/scss/brightloop_styles.scss  # Modern SaaS SCSS stylesheet
│   └── demo/
│       └── brightloop_demo_data.xml         # Sample plans, products & contracts
├── config/
│   └── odoo.conf.example                    # Production configuration template
├── dataset/                                 # Synthetic Dataset & Data Loaders
│   ├── generate_synthetic_data.py           # Reproducible generator (500 cust, 1,000 subs)
│   ├── load_synthetic_data_odoo.py          # Safety-guarded dev loading script
│   ├── dataset_documentation.md             # Complete data dictionary & ML documentation
│   ├── customers.csv                        # 500 synthetic customer accounts
│   ├── plans.csv                            # 5 subscription plans
│   ├── subscriptions.csv                    # 1,000 subscription records
│   ├── subscription_lines.csv               # 602 seat / add-on lines
│   ├── invoices.csv                         # 4,666 12-month billing invoices
│   ├── payments.csv                         # 4,666 payment transactions (91.9% paid)
│   ├── customer_behavior_metrics.csv        # ML churn feature engineering table
│   └── brightloop_synthetic_dataset.json    # Consolidated JSON payload
├── docs/                                    # Comprehensive Documentation Suite
│   ├── TECHNICAL_DOCUMENTATION.md           # Developer & Architecture Reference Manual
│   ├── USER_GUIDE.md                        # Admin, Manager & Customer User Guide
│   ├── DEPLOYMENT_GUIDE.md                  # DevOps, Docker, PostgreSQL & Disaster Recovery
│   ├── SECURITY_AND_QA_AUDIT_REPORT.md      # Security Audit, ACL Matrix & QA Report
│   ├── PRODUCT_INNOVATION_AND_INTELLIGENT_ANALYTICS.md # Innovation & Predictive Scoring
│   └── HACKATHON_PRESENTATION_AND_EVALUATION_GUIDE.md  # Presentation & Evaluation Script
├── tests/
│   ├── test_subscription_workflows.py       # 10 lifecycle & workflow automated test scenarios
│   └── test_full_system_integration.py      # 9 integration QA & performance benchmark tests
├── docker-compose.yml                       # One-click Dockerized production deployment
├── verify_backend.py                        # Automated AST, XML, and ACL test runner
└── README.md
```

---

## 🧪 Testing & Quality Assurance

All 19 test scenarios are automated and passing with 100% success:

```bash
# 1. Verify all Python AST, XML views, and security ACLs:
python verify_backend.py

# 2. Run the 10 Business Workflow Automation Scenarios:
python tests/test_subscription_workflows.py

# 3. Run the Full System Integration, Security & Performance Benchmark:
python tests/test_full_system_integration.py
```

### Benchmark Results
* **1,000 Subscriptions Evaluated**: **0.0017 seconds** (via indexed ORM search).
* **Test Suite Execution**: 19/19 tests passed in **0.006 seconds**.
* **Component Verification**: 21 views/templates, 14 window actions, 17 menuitems, 13 security ACLs, 5 automated crons.

---

## 🚀 Quickstart & Installation

### Option A: One-Click Docker Deployment (Recommended)
```bash
git clone https://github.com/Mahadharani3003/Subscription_Management_System.git
cd Subscription_Management_System
docker compose up -d
```
Access the system at `http://localhost:8069`.

### Option B: Native Odoo Installation
Add this repository to your Odoo `--addons-path`:
```bash
odoo-bin -c /path/to/odoo.conf -d <your_db> --addons-path="/path/to/odoo/addons,./" -i brightloop_subscription
```

### Option C: Module Upgrade Command
```bash
odoo-bin -c /path/to/odoo.conf -d <your_db> --addons-path="/path/to/odoo/addons,./" -u brightloop_subscription --stop-after-init
```

### Option D: Load Synthetic Development Dataset
To populate your development instance with 500 customers, 1,000 subscriptions, and 12 months of invoice history:
```bash
python odoo-bin shell -c /path/to/odoo.conf -d <your_dev_db> < dataset/load_synthetic_data_odoo.py
```

---

## 📖 Complete Documentation Suite

Detailed guides are located in the [`docs/`](docs/) directory:
- [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md): Database schema, model relationships, state machines, and APIs.
- [User Guide](docs/USER_GUIDE.md): Step-by-step manuals for Administrators, Account Managers, and Portal Customers.
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md): Production server configuration, PostgreSQL tuning, Docker, and disaster recovery.
- [Security & QA Audit Report](docs/SECURITY_AND_QA_AUDIT_REPORT.md): Access control matrix, static analysis, and benchmark audit.
- [Product Innovation & Analytics](docs/PRODUCT_INNOVATION_AND_INTELLIGENT_ANALYTICS.md): Predictive churn scoring and customer segmentation.
- [Hackathon Presentation Guide](docs/HACKATHON_PRESENTATION_AND_EVALUATION_GUIDE.md): Step-by-step demo script and credentials.

---

## 👥 Hackathon Team & Collaboration

* **Mahadharani D (Lead Architect & Core Systems)**: [Mahadharani3003](https://github.com/Mahadharani3003)
* **Anbarasi M (Senior Frontend & UX Engineer)**: [Anbarasi2708](https://github.com/Anbarasi2708)
* **Rathimeena M (UI/UX & Customer Experience Specialist)**: [rathimeena6677-del](https://github.com/rathimeena6677-del)
* **Logesh Palanisamy (Financial & BI Analytics Engineer)**: [Logeshpalanisamy](https://github.com/Logeshpalanisamy)
* **Repository**: [https://github.com/Mahadharani3003/Subscription_Management_System](https://github.com/Mahadharani3003/Subscription_Management_System)
* **Event**: Odoo Kochi Hackathon 2026
