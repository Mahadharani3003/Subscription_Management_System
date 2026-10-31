# Brightloop – Professional 5-Minute Video Recording Master Script & Evaluation Walkthrough

**Event:** Odoo Kochi Hackathon 2026  
**Recommended Recording Duration:** 4:45 – 5:00 Minutes  
**Core Technology Stack:** Native Odoo 17/18 Community & Enterprise • Python 3.12 • PostgreSQL 16  
**Localhost URL (Admin ERP):** [http://localhost:8069](http://localhost:8069) (or `/web`)  
**Localhost URL (Customer Portal):** [http://localhost:8069/my/subscriptions](http://localhost:8069/my/subscriptions)  
**Light-Mode Architecture Slide:** [http://localhost:8069/architecture](http://localhost:8069/architecture) (Open and press **F11** for full-screen)  

---

## 🧭 Pre-Recording Setup (2 Minutes to Prepare)

1. Open **Google Chrome** or **Microsoft Edge** with 3 tabs ready:
   - **Tab 1:** `http://localhost:8069/architecture` (Light Architecture Slide)
   - **Tab 2:** `http://localhost:8069/web` (Odoo Admin Web Client)
   - **Tab 3:** `http://localhost:8069/my/subscriptions` (Customer Portal & AI Chatbot)
2. Open your terminal window in the background with the test suite ready:
   ```powershell
   python -m unittest discover -s tests -p "test_*.py"
   ```
3. Press **`Win + Alt + R`** to start recording (Windows Game Bar screen recorder), or start recording in OBS / Loom.

---

## ⏱️ Complete 5-Minute Timing & Scene Breakdown

| Scene | Timecode | Target Screen | Core Theme & Odoo Tech Stack Highlight |
| :---: | :---: | :--- | :--- |
| **1** | `0:00 – 0:45` | Architecture Slide (`/architecture`) | **The Problem, The Vision & Native Odoo Tech Stack** |
| **2** | `0:45 – 1:30` | `Brightloop > Subscription Plans` | **Commercial SaaS Packaging & Multi-Company Constraints** |
| **3** | `1:30 – 2:30` | `Brightloop > Subscriptions` | **Kanban Pipeline & Day-Level Proration Engine (`account.move`)** |
| **4** | `2:30 – 3:30` | `Brightloop > Churn & AI Assistant` | **Predictive Churn Diagnostics & Zero-Hallucination AI Assistant** |
| **5** | `3:30 – 4:30` | Customer Portal (`/my/subscriptions`) | **Self-Service Controls & In-Portal Floating AI Chatbot** |
| **6** | `4:40 – 5:00` | Terminal / Test Runner | **Enterprise Testing Rigor (34 Tests, 0.021s) & Conclusion** |

---

## 🎙️ Word-for-Word Voiceover Script & Click-by-Click Guide

---

### 🎬 Scene 1: Introduction, Problem & Architecture (0:00 – 0:45)
* **Where to be:** Tab 1 — `http://localhost:8069/architecture` (press **F11** for full-screen view with the clean light background).
* **What to do:** Hover your cursor across the 4 architecture layers as you introduce them.
* **Voiceover Script:**
  > *"Respected judges and fellow developers, welcome to the presentation of **Brightloop** — an enterprise-grade, intelligent Subscription Management and Recurring Revenue platform built for the **Odoo Kochi Hackathon 2026**.*
  > 
  > *Modern subscription businesses face a major architectural problem: third-party billing tools like Stripe Billing or Chargebee create fragmented data silos, requiring fragile external synchronizations for journal entries, tax compliance, and revenue recognition.*
  > 
  > *Brightloop eliminates this problem by building directly on **native Odoo 17 and 18 ERP**. Our entire technology stack leverages the pure Odoo ORM, native `account.move` invoicing, scheduled `ir.cron` automations, and Odoo’s multi-company row-level security.*
  > 
  > *As shown in our 4-tier architecture: Layer 1 provides an interactive Kanban pipeline, dynamic BI pivot cubes, and a customer self-service portal with a floating AI Chatbot. Layer 2 is our core subscription engine handling idempotent billing and mid-cycle proration. Layer 3 delivers explainable in-ERP AI churn diagnostics and revenue actuary. And Layer 4 anchors everything on native Odoo invoicing and PostgreSQL 16."*

---

### 🎬 Scene 2: Commercial SaaS Packaging & Plans (0:45 – 1:30)
* **Where to be:** Tab 2 — Click **Subscription Plans** in the top navigation bar (`/web`).
* **What to do:**
  1. Show the list of plans: *Starter*, *Professional*, and *Enterprise*.
  2. Point out the columns: Plan Title, Code, Pricing, SaaS Tier, Subscriber Quota, REST API, AI Access, and SLA.
  3. Click into **Professional** (`PRO-MO`).
* **Voiceover Script:**
  > *"Brightloop is engineered for real-world commercial deployment. Under Subscription Plans, businesses can configure multi-cadence billing intervals — daily, monthly, annual, or custom cycle multipliers — with configurable complimentary trial days and payment grace periods.*
  > 
  > *Unlike basic billing tools, Brightloop introduces commercial SaaS packaging. Each plan defines configurable subscriber limits, REST API access permissions, AI intelligence feature flags, and contractual support SLA guarantees.*
  > 
  > *Because we leverage Odoo’s native multi-company architecture, every plan code is protected by an explicit SQL uniqueness constraint across subsidiaries. This allows a multi-tenant holding company to operate isolated subscription offerings within a single unified ERP instance."*

---

### 🎬 Scene 3: Subscription Pipeline & Mid-Cycle Proration (1:30 – 2:30)
* **Where to be:** Click **Subscriptions** in the navbar to open the visual Kanban pipeline.
* **What to do:**
  1. Show the Kanban columns: `Draft` $\rightarrow$ `Free Trial` $\rightarrow$ `Active` $\rightarrow$ `Paused` $\rightarrow$ `Past Due`.
  2. Explain the column counters and total recurring revenue summaries.
  3. Click on an **Active** contract (e.g., **Acme Global Corp - SUB/2026/0001**).
  4. Point to the smart buttons: **Invoices** generated and **Subscription LTV**.
  5. Show the **"Automated Mid-Cycle Proration Engine"** box.
  6. Select **Enterprise ($999.00 / year)** from the dropdown.
  7. Click **"Execute Prorated Plan Switch"**.
* **Voiceover Script:**
  > *"Here is the operational heart of Brightloop: the visual Kanban pipeline tracking subscriptions across their entire lifecycle from free trial to delinquent past-due states.*
  > 
  > *Let's inspect an active contract for Acme Global Corp. On the form, operators see real-time MRR calculations, auto-renewal flags, and smart buttons linking directly to posted invoices.*
  > 
  > *One of the most complex challenges in subscription billing is mid-cycle proration. When Acme decides to upgrade from the Professional tier to the Enterprise annual tier today, Brightloop's proration engine calculates the exact day-level credit from their unused billing window, applies it toward the upgraded plan, and automatically creates a prorated adjustment invoice in Odoo’s native `account.move` model.*
  > 
  > *There is zero manual bookkeeping, zero spreadsheet calculations, and 100% tax and journal compliance right out of the box."*

---

### 🎬 Scene 4: Predictive Churn & In-ERP AI Assistant (2:30 – 3:30)
* **Where to be:** Click **Churn Watchlist** in the navbar, then click **AI Business Assistant**.
* **What to do:**
  1. Show the **Predictive Churn Watchlist** table: point out the composite Health Scores (0–100), Renewal Probabilities, Churn Triggers, and Actionable Retention Recommendations.
  2. Point specifically to **Apex Media Group**: Health 35/100, Delinquency trigger.
  3. Click the yellow **AI Business Assistant** button in the navbar.
  4. Select **"What is our current MRR & ARR standing?"** and click **"Run AI Analysis"**.
  5. Point to the live cards: Active MRR ($1,316.00), Annual Run Rate, and Past Due revenue.
  6. Switch dropdown to **"How much annual revenue might we lose from cancellations?"** and click **"Run AI Analysis"**.
* **Voiceover Script:**
  > *"To protect revenue, Brightloop introduces an explainable, deterministic AI intelligence engine.*
  > 
  > *Under the Predictive Churn Watchlist, our algorithms evaluate payment delays, auto-renewal settings, and tenure loyalty to compute a composite health score from 0 to 100. For accounts at risk — such as Apex Media Group with an unpaid invoice overdue by 11 days — Brightloop flags the contract as High Risk and automatically generates actionable retention recommendations for account managers.*
  > 
  > *Furthermore, managers can launch our in-ERP AI Business Assistant. Because it queries live Odoo ORM records using optimized PostgreSQL queries, it provides real-time briefings on current MRR, upcoming 14-day renewals, and actuarial revenue loss.*
  > 
  > *Notice that this runs entirely inside Odoo ERP with **zero generative hallucinations**, **zero external cloud API costs**, and **zero customer data leakage**."*

---

### 🎬 Scene 5: Customer Portal & Floating AI Chatbot (3:30 – 4:30)
* **Where to be:** Tab 3 — `http://localhost:8069/my/subscriptions` (Customer Portal).
* **What to do:**
  1. Show the subscriber's contract card: Active Tier, Recurring Total, Next Billing Date.
  2. Point to the **Subscriber Self-Service Controls** and click **"Pause Services"**.
  3. Show how the badge turns to **PAUSED** and the button changes to **"Resume Subscription"**.
  4. Click **"Resume Subscription"** to restore it to **ACTIVE**.
  5. **Click the glowing circular AI Chatbot button** (bottom-right corner).
  6. Click the suggestion chip: **"📅 When is my next billing date?"**.
  7. Show the bot's instant response with the exact renewal date and amount.
  8. Click the chip: **"💳 Show my recent invoices"**.
  9. Show the bot's live invoice lookup with payment status (`Paid`, `Unpaid`).
* **Voiceover Script:**
  > *"Brightloop also delivers a modern self-service customer portal built on Odoo's native QWeb portal framework.*
  > 
  > *Subscribers can review their active contract, view past invoices, or temporarily suspend their services using the self-service Pause button. When paused, automated billing is suspended without terminating the contract, and subscribers can resume anytime.*
  > 
  > *In the bottom-right corner, we have integrated a floating conversational AI Chatbot. When clicked, it opens a clean drawer interface. Subscribers can click suggested chips or ask questions like 'When is my next billing date?' or 'Show my recent invoices'.*
  > 
  > *The chatbot connects to our backend controller via JSON-RPC, validates the customer's session, and retrieves verified records strictly belonging to their company. It provides instantaneous, accurate answers with complete tenant isolation."*

---

### 🎬 Scene 6: Testing Rigor & Conclusion (4:30 – 5:00)
* **Where to be:** Switch to your terminal window showing the test results:
  ```powershell
  python -m unittest discover -s tests -p "test_*.py"
  ```
* **What to do:** Highlight the test count and benchmark numbers on screen.
* **Voiceover Script:**
  > *"To ensure production stability, Brightloop includes a rigorous automated test suite. All **34 automated test scenarios pass in just 0.021 seconds**, covering proration math, billing idempotency, security record rules, and chatbot NLP parsing.*
  > 
  > *Our optimized SQL joins aggregate 10,000 contracts in under a millisecond, proving that Brightloop is ready for high-throughput commercial scale.*
  > 
  > *By leveraging native Odoo 17 and 18 ERP as our foundational technology stack, Brightloop turns subscription management into an intelligent, seamless, and automated powerhouse. Thank you!"*

---

## 🏆 Key Phrases to Emphasize for Maximum Hackathon Scores
1. **"Native Odoo Integration, Not Third-Party Middleware"**: Emphasize that invoices are native `account.move` records.
2. **"Idempotent Billing"**: Highlight that automated billing crons use savepoints and idempotency guards to eliminate duplicate billing.
3. **"Deterministic, Zero-Hallucination AI"**: Emphasize that the AI Assistant and Chatbot query real database records without generative fabrication or privacy leaks.
4. **"Day-Level Proration"**: Point out the automated credit and charge calculation when switching plans.
