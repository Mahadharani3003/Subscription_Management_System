# Brightloop – End-User Operational Manual & Administrator Guide
## Step-by-Step Workflows for System Administrators, Account Managers, and Portal Customers
**Odoo Kochi Hackathon 2026**

---

### Table of Contents
1. [User Personas & Role Matrix](#1-user-personas--role-matrix)
2. [System Administrator Guide](#2-system-administrator-guide)
3. [Subscription Manager & Officer Guide](#3-subscription-manager--officer-guide)
4. [Customer Self-Service Portal Guide](#4-customer-self-service-portal-guide)
5. [Common Operations & Step-by-Step Scenarios](#5-common-operations--step-by-step-scenarios)
6. [Frequently Asked Questions (FAQ)](#6-frequently-asked-questions-faq)

---

### 1. User Personas & Role Matrix

Brightloop defines 3 distinct user roles designed for segregation of operational duties:

| Role Persona | Target User | Security Group | Menu Visibility & Privileges |
| :--- | :--- | :--- | :--- |
| **System Administrator** | CTO, IT Operations, Head of Finance | `group_brightloop_manager` | Full system access: Plan configuration, Churn Reasons, Background Crons, Security ACLs. |
| **Subscription Officer / Manager** | Sales Rep, Account Manager, Billing Specialist | `group_brightloop_user` | Operational contract management: Create contracts, process upgrades/cancellations, monitor Dunning, inspect BI Dashboards. |
| **Portal Customer** | End Subscriber, Corporate Billing Contact | `base.group_portal` | Web portal access (`/my/subscriptions`): View active subscriptions, download invoices, pause/resume contracts. |

---

### 2. System Administrator Guide

#### A. Configuring Subscription Plans
1. Navigate to **Brightloop $\rightarrow$ Configuration $\rightarrow$ Subscription Plans**.
2. Click **New** to define a tier:
   - **Plan Name**: Enter marketing name (e.g., *SaaS Pro Monthly*).
   - **Plan Code**: Enter unique alphanumeric identifier (e.g., `PRO-MO`).
   - **Recurring Product**: Select or create a service product mapped to appropriate accounting income accounts and tax tags.
   - **Billing Cadence**: Select interval unit (`Day(s)`, `Month(s)`, `Year(s)`) and interval count multiplier (e.g. `1` Month).
   - **Recurring Base Price**: Specify base subscription rate.
   - **Trial Period (Days)**: Enter trial duration (e.g. `14` for two weeks, or `0` for none).
   - **Grace Period (Days)**: Number of days customer invoices can remain past-due before suspension (standard: `7` or `14` days).
   - **Auto-Close on Failed Payment**: Check to terminate contracts that exhaust their grace period without settlement.
3. Save the plan. It is now immediately available for new contract creation.

#### B. Managing Churn Reasons
1. Navigate to **Brightloop $\rightarrow$ Configuration $\rightarrow$ Churn Reasons**.
2. Review or create structured exit categorization codes:
   - `Budget / Too Expensive`
   - `Missing Features / Capability Gap`
   - `Switching to Competitor`
   - `Company Downsized / Dissolved`
   - `Service Quality / Technical Issues`
   - `Project Ended / Temporary Need`

#### C. Verifying Automated Schedulers (Cron Jobs)
1. Navigate to **Settings $\rightarrow$ Technical $\rightarrow$ Automation $\rightarrow$ Scheduled Actions**.
2. Search for `Brightloop`:
   - `Brightloop: Automated Daily Recurring Invoicing` (Runs daily at midnight)
   - `Brightloop: Dispatch Upcoming Renewal Reminders` (Runs daily at 06:00)
   - `Brightloop: Dunning & Grace Period Monitor` (Runs daily at 07:00)
   - `Brightloop: Contract Expirations & Term Closer` (Runs daily at 23:00)
   - `Brightloop: AI Health Scoring & Churn Risk Predictor` (Runs daily at 08:00)
3. Ensure all 5 crons have the **Active** toggle turned on.

---

### 3. Subscription Manager & Officer Guide

#### A. Managing the Kanban Lifecycle Pipeline
1. Navigate to **Brightloop $\rightarrow$ Subscriptions $\rightarrow$ All Subscriptions**.
2. The Kanban pipeline groups contracts by operational stage:
   - **Draft**: Newly created proposals awaiting customer sign-off or initial activation.
   - **Free Trial**: Subscribers experiencing complimentary trial periods.
   - **Active**: Paying, good-standing subscriptions with automated recurring billing.
   - **Paused**: Temporarily suspended contracts; recurring invoices will **not** be generated.
   - **Past Due**: Delinquent accounts with unsettled invoices within their grace period.
   - **Cancelled**: Terminated contracts with documented churn reason codes.
   - **Closed**: Completed fixed-term subscriptions that reached their natural end date.

#### B. Performing a Prorated Plan Upgrade or Downgrade
1. Open any contract in `Active`, `Free Trial`, or `Past Due` status.
2. In the top action bar, click **Upgrade / Change Plan**.
3. Select the **New Target Plan** from the modal dialog.
4. The system automatically computes:
   - Cycle elapsed days and remaining days.
   - Unused credit remaining on the existing plan.
   - Prorated charge for the new tier.
   - **Net Prorated Adjustment Amount**.
5. Click **Apply Plan Change**:
   - The contract's tier and recurring total are immediately updated.
   - An immediate invoice (or credit note) is drafted for the prorated difference.
   - A confirmation email is dispatched to the subscriber.

#### C. Handling Cancellations with Structured Offboarding
1. Open the subscription and click **Cancel Contract**.
2. Select the primary **Reason for Cancellation** from the drop-down.
3. Enter optional **Cancellation Notes** detailing customer feedback.
4. Click **Confirm Cancellation**:
   - Contract transitions to `Cancelled`.
   - Recurring billing is permanently deactivated.
   - An exit confirmation email is sent to the customer.

#### D. Monitoring the Predictive Churn Watchlist
1. Navigate to **Brightloop $\rightarrow$ Reporting & Analytics $\rightarrow$ Predictive Churn Watchlist**.
2. The system surfaces all active contracts flagged with `High` or `Medium` churn hazard sorted by Health Score ascending.
3. Review the **Risk Diagnostic Factors** on the contract (e.g. *"2 unpaid invoices | Auto-renew disabled"*).
4. Take proactive retention action (e.g., call customer, adjust pricing, or send customized offer) before the customer cancels.

---

### 4. Customer Self-Service Portal Guide

Customers access the portal by visiting `https://your-domain.com/my`:

1. **Dashboard Overview**:
   - Click the **Subscriptions** tile to view all contracts associated with the account.
2. **Reviewing Contract Details**:
   - Click any subscription reference (e.g., `SUB/2026/00001`).
   - View base tier price, billing interval, and exact next renewal date.
   - Inspect active add-on seat lines and allocated licenses.
   - Review past billing invoices with real-time settlement status (`Paid`, `Unpaid`).
3. **Pausing Services**:
   - If taking a business hiatus, click **Pause Services**.
   - Status instantly transitions to `Paused`; no recurring invoices will be billed while paused.
4. **Resuming Services**:
   - Click **Resume Subscription** whenever ready to restore full service access.

---

### 5. Common Operations & Step-by-Step Scenarios

#### Scenario 1: Adding Additional User Seats to an Existing Contract
1. Open the active subscription in the backend.
2. Under the **Add-on Lines & Seat Metering** tab, click **Add a line**.
3. Select the **Product** (e.g., *Additional Team Seat*), enter **Quantity** (e.g. `5`), and **Unit Price** (e.g. `$10.00`).
4. Click Save. The contract's `Recurring Total`, `MRR`, and `ARR` update automatically. The next recurring invoice will include these add-on seats.

#### Scenario 2: Recovering an Overdue Account
1. Customer settles an outstanding overdue invoice via bank transfer or online payment.
2. When the payment is registered on the native Odoo `account.move`, Brightloop's payment hook automatically inspects the subscription.
3. If no other unpaid invoices remain, the subscription's status is automatically restored from `Past Due` back to `Active` with zero human intervention required.

---

### 6. Frequently Asked Questions (FAQ)

**Q: Does Brightloop support custom multi-year contracts?**  
A: Yes! Configure a plan with `Billing Interval = Year(s)` and `Billing Interval Count = 2` or `3` for biennial or triennial billing.

**Q: Can a contract be billed manually before the scheduled date?**  
A: Yes. Authorized managers can click **Generate Recurring Invoice** on the subscription form. Brightloop's idempotency safeguard ensures only one invoice is generated for any given billing cycle.

**Q: What happens if a customer has multiple subscriptions?**  
A: Both the backend customer form ([`res.partner`](file:///C:/Users/mahad/.gemini/antigravity-ide/scratch/brightloop/brightloop_subscription/models/res_partner.py)) and the web portal (`/my/subscriptions`) list all contracts owned by the customer, with cumulative LTV and health tracking.
