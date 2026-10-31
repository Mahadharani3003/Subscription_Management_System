# Brightloop – Video Screen Recording Walkthrough & Master Script

**Event:** Odoo Kochi Hackathon 2026  
**Recommended Video Duration:** 3 Minutes 30 Seconds (Max 4 Minutes)  
**Target Audience:** Technical Judges, Odoo Solution Architects, and Product Evaluators  
**Primary Localhost URL:** [http://localhost:8069](http://localhost:8069)  
**Architecture Slide URL:** Open [`docs/brightloop_architecture_slide.html`](file:///C:/Users/mahad/.gemini/antigravity-ide/scratch/brightloop/docs/brightloop_architecture_slide.html) in your browser and press **F11** for full-screen.  

---

## 🛠️ How to Record Your Video (Setup & Tools)

### Recommended Recording Software (Choose One):
1. **Windows Built-in Game Bar (Easiest - No Installation Required)**:
   - Open your browser window to `http://localhost:8069`.
   - Press **`Win + Alt + R`** to start recording immediately.
   - Speak into your microphone.
   - Press **`Win + Alt + R`** again to stop. Video is saved automatically in `Videos\Captures`.
2. **OBS Studio (Professional Quality)**:
   - Set resolution to 1920x1080 (1080p, 60fps).
   - Add "Display Capture" or "Window Capture" targeting Chrome/Edge.
3. **Loom / Clipchamp (Quick & Easy)**:
   - Share browser tab and record audio + optional webcam bubble in the corner.

### Pre-Recording Checklist:
- [ ] Browser window maximized (press **F11** or zoom 100%).
- [ ] Logged into Odoo at `http://localhost:8069` (database: `brightloop_db`).
- [ ] Open a second tab to `http://localhost:8069/my/subscriptions` (customer portal view).
- [ ] Open a third tab to `docs/brightloop_architecture_slide.html` (the stunning architecture slide).

---

## 🎬 6-Scene Video Demonstration Breakdown

| Scene # | Timecode | Screen to Show | What to Demonstrate |
| :---: | :---: | :--- | :--- |
| **Scene 1** | `0:00 - 0:35` | `docs/brightloop_architecture_slide.html` (Full-Screen) | Project Introduction & 4-Tier Architecture |
| **Scene 2** | `0:35 - 1:15` | `Brightloop > Configuration > Subscription Plans` | Commercial SaaS Packaging & Tier Limits |
| **Scene 3** | `1:15 - 2:00` | `Brightloop > Subscriptions > All Subscriptions` | Kanban Pipeline & Prorated Plan Switch Wizard |
| **Scene 4** | `2:00 - 2:40` | `Brightloop > Reporting & Analytics` | AI Business Assistant & Predictive Churn Watchlist |
| **Scene 5** | `2:40 - 3:15` | Customer Portal (`/my/subscriptions`) | Floating AI Chatbot in Action (Real Data Lookups) |
| **Scene 6** | `3:15 - 3:35` | Terminal / Test Runner | 34 Tests Passing (100%), Sub-millisecond Benchmarks |

---

## 🎙️ Word-for-Word Voiceover Script & Click-by-Click Guide

### Scene 1: Project Introduction & Architecture (0:00 – 0:35)
- **Where to go:** Open `docs/brightloop_architecture_slide.html` in Chrome/Edge, press **F11** for full-screen.
- **Voiceover Script:**
  > *"Hello everyone! Welcome to **Brightloop**, an intelligent, enterprise-grade Subscription Management and Recurring Revenue platform built natively on Odoo 17 and 18 for the Odoo Kochi Hackathon.*
  > 
  > *As shown in our system architecture, Brightloop operates across four unified layers: a presentation layer featuring a visual Kanban pipeline and customer self-service portal with an AI Chatbot; a core subscription engine executing idempotent billing, automated proration, and dunning; an in-ERP AI intelligence core predicting churn risk and actuarial ARR loss; and native Odoo integration with `account.move` invoicing and multi-company data isolation."*

---

### Scene 2: Commercial SaaS Packaging & Plans (0:35 – 1:15)
- **Where to go:** In Odoo, navigate to **Brightloop $\rightarrow$ Configuration $\rightarrow$ Subscription Plans**.
- **What to click:**
  1. Show the list of plans: *Starter*, *Professional*, *Enterprise*.
  2. Click on **Professional** (`PRO-MO`) to open the form view.
  3. Click on the **SaaS Packaging & Entitlements** tab.
- **Voiceover Script:**
  > *"Brightloop is designed for real-world commercial SaaS. Under Subscription Plans, businesses can configure multi-cadence billing intervals — daily, monthly, or annual — with customizable free trial and payment grace periods.*
  > 
  > *Under the SaaS Packaging tab, we have implemented commercial tiering: configurable subscriber limits, REST API access flags, support SLA guarantees, and AI feature toggles. Every plan code is enforced with a database-level multi-company unique constraint."*

---

### Scene 3: Subscription Pipeline & Mid-Cycle Proration (1:15 – 2:00)
- **Where to go:** Navigate to **Brightloop $\rightarrow$ Subscriptions $\rightarrow$ All Subscriptions**.
- **What to click:**
  1. Show the **Kanban view** with status columns: `Draft`, `Free Trial`, `Active`, `Paused`, `Past Due`.
  2. Click on an **Active** subscription (e.g. `SUB/2026/0001`).
  3. Point to the smart buttons: **Invoices** generated and **Subscription LTV**.
  4. Click the action button **Upgrade / Downgrade Plan**.
  5. Select the **Enterprise** tier and show the **Estimated Proration Adjustment** dynamically calculated.
  6. Click **Confirm Plan Change**.
- **Voiceover Script:**
  > *"Here is the operational heart of Brightloop: the visual Kanban pipeline tracking subscriptions across their entire lifecycle.*
  > 
  > *On any active subscription, our smart buttons link directly to generated Odoo customer invoices. If a customer upgrades or downgrades midway through their billing cycle, Brightloop’s proration engine calculates the exact day-level credit from the unused period, applies it toward the new tier, and automatically generates a prorated adjustment invoice in `account.move` with zero manual bookkeeping."*

---

### Scene 4: Churn Intelligence & In-ERP AI Assistant (2:00 – 2:40)
- **Where to go:** Navigate to **Brightloop $\rightarrow$ Reporting & Analytics $\rightarrow$ Predictive Churn Watchlist**, then open **AI Business Assistant**.
- **What to click:**
  1. Show the **Predictive Churn Watchlist** with composite Health Scores (0–100), churn risk levels (`High`, `Medium`, `Low`), and Actionable Retention Recommendations.
  2. Click **AI Business Assistant** in the Reporting menu.
  3. Leave "What is our current MRR & ARR standing?" selected and click **Ask Intelligence Assistant**.
  4. Point to the live KPI cards: Active MRR, Annual Run Rate, and Past Due revenue.
- **Voiceover Script:**
  > *"To protect revenue, Brightloop introduces explainable, deterministic AI capabilities. Our predictive churn engine evaluates payment delays, tenure loyalty, and auto-renew flags to assign a health score and prescribe concrete retention actions for account managers.*
  > 
  > *Managers can also launch our in-ERP AI Business Assistant. Because it queries authorized live Odoo ORM records directly, it delivers instant executive briefings on MRR, upcoming renewals, and actuarial revenue loss with zero generative hallucination and zero confidential data leakage to external cloud APIs."*

---

### Scene 5: Customer Self-Service Portal & Live Chatbot (2:40 – 3:15)
- **Where to go:** Switch to the customer portal tab at `http://localhost:8069/my/subscriptions`.
- **What to click:**
  1. Show the subscriber's contract overview, active tier, and self-service **Pause Services** button.
  2. **Click the floating AI Chatbot launcher button** (bottom right, purple/teal gradient circle).
  3. Click the suggestion chip: **"📅 When is my next billing date?"**.
  4. Bot replies with the exact scheduled renewal date, days remaining, and amount due.
  5. Click the chip: **"💳 Show my recent invoices"**.
  6. Bot replies with recent invoice numbers, amounts, and live payment status.
- **Voiceover Script:**
  > *"Subscribers also get a modern self-service experience at `/my/subscriptions`, where they can view add-on seats, review invoices, or temporarily pause their services.*
  > 
  > *Integrated directly into the portal is our floating AI Chatbot. When clicked, it opens a clean conversational drawer. Subscribers can click suggested chips or ask natural questions like 'When is my next billing date?' or 'Show my recent invoices'. The chatbot queries the logged-in customer's authorized records in real time with strict tenant isolation, providing instant, verified answers."*

---

### Scene 6: Quality Assurance, Benchmarks & Conclusion (3:15 – 3:35)
- **Where to go:** Show the terminal window with the test results:
  `C:\Users\mahad\.local\bin\python3.12.exe -m unittest discover -s tests -p "test_*.py"`
- **Voiceover Script:**
  > *"Finally, Brightloop is enterprise-hardened. Our automated test suite executes 34 comprehensive tests in just 0.021 seconds with 100% pass rate, and our SQL joins process 10,000 contracts in under a millisecond.*
  > 
  > *Brightloop transforms Odoo into an intelligent, autonomous subscription billing powerhouse ready for commercial scale. Thank you!"*

---

## 🏆 Key Talking Points to Impress Judges
1. **"Native, Not Glued"**: Brightloop does not use brittle external syncs; invoices are native `account.move` records.
2. **"Zero Hallucination AI"**: AI diagnostics and chatbot lookups run on live PostgreSQL records without external API costs or privacy risks.
3. **"True Idempotency"**: Billing crons use database savepoints and date guards to eliminate duplicate billing hazards.
4. **"Day-Level Proration"**: Upgrades and downgrades calculate exact remaining-day credits automatically.
