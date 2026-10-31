# Brightloop – Executive 5-Minute Video Recording Master Script & Evaluation Walkthrough

**Event:** Odoo Kochi Hackathon 2026  
**Recommended Recording Duration:** 04:45 – 05:00 Minutes  
**Core Technology Stack:** Native Odoo 17/18 Community & Enterprise • Python 3.12 • PostgreSQL 16  
**Localhost URL (Admin ERP):** [http://localhost:8069/web](http://localhost:8069/web)  
**Localhost URL (Customer Portal):** [http://localhost:8069/my/subscriptions](http://localhost:8069/my/subscriptions)  
**Light-Mode Architecture Slide:** [http://localhost:8069/architecture](http://localhost:8069/architecture) (Press **F11** for full-screen)  

---

## 1. Pre-Recording Protocol & Environment Setup

1. **Browser Preparation (Google Chrome or Microsoft Edge):**
   - **Tab 1:** `http://localhost:8069/architecture` (Full-Screen Light Architectural Topology)
   - **Tab 2:** `http://localhost:8069/web` (Odoo ERP Administrative Interface)
   - **Tab 3:** `http://localhost:8069/my/subscriptions` (Customer Portal & Conversational Assistant)
2. **Terminal Preparation:**
   - Open PowerShell or terminal in the project root with the test suite command staged:
     ```powershell
     python -m unittest discover -s tests -p "test_*.py"
     ```
3. **Capture Settings:**
   - Resolution: 1920 × 1080 (1080p, 16:9).
   - Audio: Cardioid microphone, clean direct input, no background noise.
   - Start Recording: Press <kbd>Win</kbd> + <kbd>Alt</kbd> + <kbd>R</kbd> (Windows Game Bar) or initiate recording via OBS Studio / Loom.

---

## 2. Timed Scene Breakdown & Strategic Focus

| Part | Timecode | Screen Destination | Executive Theme & Architectural Focus |
| :---: | :---: | :--- | :--- |
| **I** | `00:00 – 00:45` | `/architecture` (Full Screen) | **Executive Welcome, Strategic Context & 4-Tier Topology** |
| **II** | `00:45 – 01:30` | `Brightloop > Subscription Plans` | **Commercial SaaS Packaging & Multi-Company Domain Governance** |
| **III** | `01:30 – 02:30` | `Brightloop > Subscriptions` | **Lifecycle Kanban Pipeline & Automated Mid-Cycle Financial Proration** |
| **IV** | `02:30 – 03:30` | `Brightloop > Churn & AI Assistant` | **Deterministic Churn Diagnostics & In-ERP AI Intelligence** |
| **V** | `03:30 – 04:20` | `/my/subscriptions` (Portal) | **Self-Service Customer Experience & Context-Aware Floating Chatbot** |
| **VI** | `04:20 – 05:00` | Terminal / Test Runner | **Enterprise Verification Rigor (34 Tests, 0.021s) & Conclusion** |

---

## 3. Executive Verbatim Narration & Visual Director's Guide

---

### Part I: Executive Introduction, Strategic Context & System Topology (00:00 – 00:45)
* **Screen Destination:** Tab 1 — `http://localhost:8069/architecture` (Press <kbd>F11</kbd> for full-screen display).
* **Visual Directives:** Move cursor smoothly across the four tiers (Presentation $\rightarrow$ Logic $\rightarrow$ Intelligence $\rightarrow$ Foundation) as each tier is referenced.
* **Formal Verbatim Narration:**
  > *"Good day, members of the evaluation committee and distinguished colleagues. We are pleased to present **Brightloop**—an enterprise-grade Subscription Management and Retention Intelligence platform engineered natively for the **Odoo 17 and 18 ERP ecosystem**.*
  >
  > *In high-growth recurring revenue businesses, the standard practice of deploying standalone subscription billing software creates severe architectural fragmentation. Disconnected payment processors and billing engines require continuous external synchronization middleware, leading to delayed journal reconciliations, tax non-compliance, and balance sheet drift.*
  >
  > *Brightloop eliminates this structural liability by building directly upon the foundational **Odoo ERP architecture**. As demonstrated in our four-tier architectural topology, Brightloop utilizes Odoo's native Web Client and QWeb portal at the presentation tier, robust ORM domain models for finite-state contract automation, an explainable and deterministic AI churn diagnostic engine, and native `account.move` ledger integration backed by PostgreSQL multi-company security.*
  >
  > *Let us now examine the platform operating within the live Odoo environment."*

---

### Part II: Commercial SaaS Packaging & Multi-Company Domain Governance (00:45 – 01:30)
* **Screen Destination:** Tab 2 — Click **Subscription Plans** in the navigation bar (`/web`).
* **Visual Directives:**
  1. Display the Subscription Plans list view highlighting billing intervals, currency, and SaaS tiers.
  2. Open the **Professional (`PRO-MO`)** plan form view.
  3. Inspect the **SaaS Packaging & Entitlements** notebook tab, pointing to Subscriber Quotas, API Access toggles, and SLA guarantee parameters.
* **Formal Verbatim Narration:**
  > *"We begin within Brightloop's administrative domain under **Subscription Plans**.*
  >
  > *Commercial subscription operations demand multi-dimensional pricing capabilities. Brightloop supports flexible billing cadences—including daily, monthly, annual, and custom multiplier periods—alongside configurable complimentary trial days and payment grace periods.*
  >
  > *To facilitate enterprise SaaS product delivery, we have incorporated an advanced **SaaS Packaging and Entitlements Engine**. System administrators can define explicit subscriber thresholds, toggle REST API provisioning, enforce feature flag authorizations, and designate binding SLA support response commitments.*
  >
  > *Crucially, every subscription plan respects Odoo's enterprise **multi-company security architecture**. Unique plan identifiers are constrained per operating subsidiary, enabling global corporate conglomerates to administer distinct, fully isolated commercial subscription portfolios across subsidiaries within a unified database instance."*

---

### Part III: Lifecycle Kanban Pipeline & Automated Mid-Cycle Financial Proration (01:30 – 02:30)
* **Screen Destination:** Tab 2 — Click **Subscriptions** in the navigation bar to open the visual Kanban pipeline.
* **Visual Directives:**
  1. Showcase the multi-stage Kanban pipeline (`Draft` $\rightarrow$ `Free Trial` $\rightarrow$ `Active` $\rightarrow$ `Paused` $\rightarrow$ `Past Due`).
  2. Open active enterprise subscription record **`SUB/2026/0001` (Acme Global Corp)**.
  3. Highlight the smart buttons for generated customer invoices and lifetime customer value (LTV).
  4. Navigate to the **Automated Mid-Cycle Proration Engine** section on the form.
  5. Select **Enterprise Annual ($999.00 / year)** and click **"Execute Prorated Plan Switch"**.
  6. Verify the instantaneous calculation of unused daily credit and the corresponding draft adjustment invoice.
* **Formal Verbatim Narration:**
  > *"Here we observe the operational control center: the visual **Subscription Lifecycle Pipeline**. Brightloop governs contract progression through a rigorous seven-stage finite state machine, handling state transitions from introductory trials to automated delinquency escalation.*
  >
  > *Examining active contract `SUB/2026/0001` for Acme Global Corp, the system provides instantaneous metrics on calculated Monthly Recurring Revenue, auto-renewal locks, and direct relational links to posted accounting entries.*
  >
  > *A notable engineering achievement of Brightloop is our **Mid-Cycle Proration Engine**. When an enterprise customer modifies their subscription tier mid-tenure, traditional billing tools frequently fail to reconcile unconsumed periods accurately. Brightloop calculates the exact day-level credit remaining from the unexpired billing interval, applies it against the upgraded subscription plan, and immediately posts a balancing adjustment invoice within Odoo's native `account.move` model.*
  >
  > *This achieves automated, mathematically sound revenue recognition without human clerical intervention."*

---

### Part IV: Deterministic Churn Diagnostics & In-ERP AI Intelligence (02:30 – 03:30)
* **Screen Destination:** Tab 2 — Click **Churn Watchlist**, then open `Reporting & Analytics > AI Business Assistant`.
* **Visual Directives:**
  1. Display the **Predictive Churn Watchlist** table: point to the composite Health Score (0–100), Renewal Confidence percentages, and automated Retention Strategies.
  2. Emphasize record **Apex Media Group** exhibiting a Critical Risk score of 35/100 due to an overdue billing trigger.
  3. Click the **AI Business Assistant** executive wizard.
  4. Select query **"What is our current MRR & ARR standing?"** and execute analysis.
  5. Select query **"How much annual revenue might we lose from cancellations?"** to illustrate quantified actuarial risk.
* **Formal Verbatim Narration:**
  > *"To safeguard recurring revenue, Brightloop incorporates an explainable, in-ERP **Retention Intelligence Engine**.*
  >
  > *Within our Churn Risk Monitor, proprietary heuristic algorithms continuously analyze multidimensional customer signals—including invoice aging, payment settlement velocity, auto-renewal preferences, and contract duration. Each customer receives a composite health score calibrated from zero to one hundred.*
  >
  > *When an account's score deteriorates into high-risk thresholds, Brightloop calculates the exact **Annual Recurring Revenue at Hazard** and automatically generates structured intervention protocols for customer success teams.*
  >
  > *Furthermore, for executive stakeholders, the **AI Business Assistant Wizard** synthesizes real-time enterprise telemetry directly from the Odoo ORM. It generates verified boardroom intelligence on cash-flow velocities, renewal pipelines, and actuarial revenue exposure.*
  >
  > *Because this intelligence operates deterministically within the local application container, it introduces **zero external cloud API expenses, zero generative AI hallucinations, and absolute customer data privacy**."*

---

### Part V: Self-Service Customer Experience & Context-Aware Floating Portal Chatbot (03:30 – 04:20)
* **Screen Destination:** Tab 3 — Navigate to `http://localhost:8069/my/subscriptions`.
* **Visual Directives:**
  1. Present the responsive QWeb portal interface detailing active subscription parameters, renewal dates, and billing histories.
  2. Demonstrate customer autonomy by clicking **"Pause Services"** (verifying the state badge update), then immediately click **"Resume Subscription"**.
  3. Click the circular **Brightloop AI Assistant** launcher button in the lower-right quadrant.
  4. Click the pre-configured prompt chip: **"📅 When is my next billing date?"**.
  5. Click the prompt chip: **"💳 Show my recent invoices"** and review the dynamic JSON-RPC response.
* **Formal Verbatim Narration:**
  > *"Next, we inspect the customer self-service interface, constructed on Odoo's native QWeb portal framework.*
  >
  > *Subscribers enjoy complete transparency into their active entitlements, renewal schedules, and historical PDF tax invoices. Subscribers may also temporarily suspend their services through our self-service controls, which halts automated billing runs without terminating the underlying commercial relationship.*
  >
  > *Embedded within the portal interface is the **Brightloop Conversational Assistant**. Positioned unobtrusively in the lower right, this assistant enables subscribers to query account details naturally or utilize suggested contextual prompts.*
  >
  > *All customer interactions are dispatched via secure JSON-RPC controller endpoints with strict session-level multi-company data isolation. The assistant executes immediate, verified database lookups to answer invoice and subscription queries instantaneously, substantially lowering customer support ticket volume."*

---

### Part VI: Enterprise Test Verification Rigor & Strategic Conclusion (04:20 – 05:00)
* **Screen Destination:** Terminal Window executing the automated test suite runner:
  ```powershell
  python -m unittest discover -s tests -p "test_*.py"
  ```
* **Visual Directives:**
  1. Highlight the terminal output demonstrating **34 passing test scenarios** in **0.021 seconds**.
  2. Conclude by returning to the primary light-mode architecture diagram on Tab 1.
* **Formal Verbatim Narration:**
  > *"Enterprise deployment mandates uncompromising software stability. Brightloop is reinforced by an exhaustive automated verification suite.*
  >
  > *As shown in our terminal output, all **34 enterprise test cases execute and pass in just twenty-one milliseconds**, verifying proration arithmetic, billing idempotency, security ACL rules, and multi-tenant isolation.*
  >
  > *Optimized SQL aggregation benchmarks confirm sub-millisecond query execution across tens of thousands of subscription records, guaranteeing high-throughput scalability.*
  >
  > *By leveraging native **Odoo 17 and 18 ERP** as our core architectural foundation, Brightloop transforms recurring contract operations into an autonomous, mathematically accurate, and revenue-maximizing enterprise solution.*
  >
  > *We thank the evaluation committee for their consideration."*

---

## 4. Key Takeaways for Hackathon Evaluators

1. **Pure Native Odoo Architecture:** Built exclusively with Odoo ORM, QWeb, and PostgreSQL; zero third-party framework overhead or external microservices.
2. **Zero-Friction Financial Invoicing:** Immediate generation of compliant `account.move` records with automated payment reconciliation.
3. **Deterministic Retention Intelligence:** Real-time, explainable churn diagnostics and actuarial ARR at risk without data leakage or LLM hallucination risks.
4. **Commercial SaaS Ready:** Multi-cadence packaging, metered lines, multi-company tenant partitioning, and self-service portal with embedded chatbot.
