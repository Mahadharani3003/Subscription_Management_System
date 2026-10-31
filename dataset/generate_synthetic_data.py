# -*- coding: utf-8 -*-
"""
Brightloop Synthetic Dataset Generator
======================================
Generates 500 customers, 5 plans, 1,000 subscriptions, 12 months of invoice & payment history,
and behavioral churn metrics for testing and ML experimentation.

Reproducible via fixed random seed (42).
All records are explicitly tagged as [SYNTHETIC].
"""

import os
import csv
import json
import random
from datetime import datetime, date, timedelta

# Fix random seed for strict reproducibility
SEED = 42
random.seed(SEED)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Anchor Date: 2026-10-31
ANCHOR_DATE = date(2026, 10, 31)
START_WINDOW_DATE = ANCHOR_DATE - timedelta(days=365) # 12 months prior

# --- Reference Lists for Generation ---
COMPANY_PREFIXES = [
    "Apex", "BlueWave", "CloudPeak", "DeltaByte", "EchoSphere", "Falcon", "GridCore",
    "Horizon", "IronClad", "Jupiter", "Krypton", "Luminary", "MetaFlow", "NovaPulse",
    "OmniLink", "Prism", "Quantum", "Radiant", "SyncPulse", "TerraData", "Unified",
    "Vanguard", "WarpSpeed", "Zenith", "Aether", "Boreal", "Cobalt", "Dynamo", "Everest",
    "Fortis", "Galactic", "Hyperion", "Infini", "JetStream", "Kinetic", "LogiTech",
    "Matrix", "Nexus", "Optima", "Polaris", "Quasar", "Resonant", "Strata", "Titan"
]

COMPANY_SUFFIXES = [
    "Technologies", "Solutions", "Networks", "Labs", "Digital", "Systems", "Media",
    "Software", "Analytics", "Enterprises", "Ventures", "Consulting", "Platform",
    "Logistics", "Health", "Fintech", "Security", "Robotics", "Cloud", "Interactive"
]

INDUSTRIES = [
    "SaaS & Cloud Services", "FinTech & Banking", "E-Commerce & Retail",
    "HealthTech & Life Sciences", "Logistics & Supply Chain",
    "EdTech & E-Learning", "Digital Marketing & Media", "Manufacturing & IoT"
]

CITIES = [
    ("Kochi", "India", "Asia/Kolkata"),
    ("Bangalore", "India", "Asia/Kolkata"),
    ("Mumbai", "India", "Asia/Kolkata"),
    ("Singapore", "Singapore", "Asia/Singapore"),
    ("Dubai", "UAE", "Asia/Dubai"),
    ("London", "United Kingdom", "Europe/London"),
    ("Berlin", "Germany", "Europe/Berlin"),
    ("New York", "United States", "America/New_York"),
    ("San Francisco", "United States", "America/Los_Angeles"),
    ("Sydney", "Australia", "Australia/Sydney")
]

CHURN_REASONS = [
    ("BUDGET", "Budget Constraints / Downsizing", 0.30),
    ("COMPETITOR", "Migrated to Competitor", 0.28),
    ("FEATURES", "Feature Limitations / Missing Capabilities", 0.18),
    ("PAYMENT_FAILURE", "Involuntary Churn (Repeated Payment Failures)", 0.14),
    ("PROJECT_DONE", "Project Terminated / Engagement Ended", 0.10)
]

PAYMENT_FAILURE_REASONS = [
    "insufficient_funds", "card_expired", "bank_declined", "gateway_timeout", "stolen_card_flag"
]

PLANS = [
    {
        "id": "PLAN-STARTER-MO",
        "name": "Starter (Monthly)",
        "billing_interval": "month",
        "billing_interval_count": 1,
        "price": 29.00,
        "trial_period_days": 14,
        "grace_period_days": 7,
        "mrr": 29.00,
        "weight": 0.35
    },
    {
        "id": "PLAN-GROWTH-MO",
        "name": "Growth Pro (Monthly)",
        "billing_interval": "month",
        "billing_interval_count": 1,
        "price": 99.00,
        "trial_period_days": 14,
        "grace_period_days": 7,
        "mrr": 99.00,
        "weight": 0.30
    },
    {
        "id": "PLAN-SCALE-MO",
        "name": "Scale Up (Monthly)",
        "billing_interval": "month",
        "billing_interval_count": 1,
        "price": 249.00,
        "trial_period_days": 14,
        "grace_period_days": 7,
        "mrr": 249.00,
        "weight": 0.15
    },
    {
        "id": "PLAN-ENTERPRISE-YR",
        "name": "Enterprise (Annual)",
        "billing_interval": "year",
        "billing_interval_count": 1,
        "price": 1999.00,
        "trial_period_days": 30,
        "grace_period_days": 14,
        "mrr": 1999.00 / 12.0,
        "weight": 0.12
    },
    {
        "id": "PLAN-EXECUTIVE-YR",
        "name": "Executive Premium (Annual)",
        "billing_interval": "year",
        "billing_interval_count": 1,
        "price": 4999.00,
        "trial_period_days": 30,
        "grace_period_days": 14,
        "mrr": 4999.00 / 12.0,
        "weight": 0.08
    }
]

ADDON_PRODUCTS = [
    {"name": "Additional Seat Meter", "price": 10.00},
    {"name": "Dedicated IP & SSL", "price": 20.00},
    {"name": "100GB Redundant Storage", "price": 15.00},
    {"name": "Priority Support SLA", "price": 50.00}
]

def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, max(0, delta.days))
    return start + timedelta(days=random_days)

def weighted_choice(choices, weights):
    return random.choices(choices, weights=weights, k=1)[0]


def generate():
    print(f"Generating synthetic dataset anchored at {ANCHOR_DATE}...")

    # 1. Generate 500 Customers
    customers = []
    used_names = set()
    for i in range(1, 501):
        cust_id = f"CUST-SYNTH-{i:04d}"
        while True:
            c_name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)} {random.randint(10, 999)}"
            if c_name not in used_names:
                used_names.add(c_name)
                break
        city, country, tz = random.choice(CITIES)
        industry = random.choice(INDUSTRIES)
        domain = c_name.lower().replace(" ", "").replace("&", "")[:12] + ".test"
        
        # Customer creation date in trailing 24 months
        created_date = random_date(ANCHOR_DATE - timedelta(days=730), ANCHOR_DATE - timedelta(days=30))

        customers.append({
            "customer_id": cust_id,
            "name": f"[SYNTHETIC] {c_name}",
            "email": f"billing@{domain}",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "city": city,
            "country": country,
            "timezone": tz,
            "industry": industry,
            "created_date": created_date.isoformat(),
            "is_synthetic": True,
            "data_tag": "SYNTHETIC_DEV_DATA"
        })

    # 2. Generate 1,000 Subscriptions across 12 months
    subscriptions = []
    sub_lines = []
    invoices = []
    payments = []
    behavior_metrics = {c["customer_id"]: {
        "customer_id": c["customer_id"],
        "customer_name": c["name"],
        "industry": c["industry"],
        "country": c["country"],
        "tenure_days": (ANCHOR_DATE - date.fromisoformat(c["created_date"])).days,
        "subscription_count": 0,
        "active_subscription_count": 0,
        "total_invoices": 0,
        "total_invoices_paid": 0,
        "total_invoices_failed": 0,
        "total_revenue_paid": 0.0,
        "upgrades_count": 0,
        "downgrades_count": 0,
        "support_tickets_count": random.randint(0, 15),
        "avg_platform_logins_monthly": round(random.uniform(2.5, 48.0), 1),
        "is_churned": 0,
        "churn_reason": "N/A"
    } for c in customers}

    plan_weights = [p["weight"] for p in PLANS]
    sub_counter = 1

    for i in range(1, 1001):
        sub_ref = f"SUB/2026/{i:05d}"
        cust = random.choice(customers)
        cust_id = cust["customer_id"]
        bm = behavior_metrics[cust_id]
        bm["subscription_count"] += 1

        selected_plan = weighted_choice(PLANS, plan_weights)
        
        # Start date distributed within the past 12 months
        start_date = random_date(START_WINDOW_DATE, ANCHOR_DATE - timedelta(days=10))

        # Target outcome distribution:
        # active (55%), cancelled (25%), trial (8%), past_due (7%), paused (5%)
        outcome = random.choices(
            ["active", "cancelled", "trial", "past_due", "paused"],
            weights=[0.55, 0.25, 0.08, 0.07, 0.05],
            k=1
        )[0]

        trial_end_date = None
        if selected_plan["trial_period_days"] > 0:
            trial_end_date = start_date + timedelta(days=selected_plan["trial_period_days"])

        end_date = None
        paused_date = None
        churn_code = ""
        churn_label = 0
        cancellation_notes = ""

        # Modifiers for upgrades / downgrades
        has_upgrade = random.random() < 0.12
        has_downgrade = (not has_upgrade) and (random.random() < 0.04)
        if has_upgrade:
            bm["upgrades_count"] += 1
        if has_downgrade:
            bm["downgrades_count"] += 1

        # Determine state-specific dates & details
        if outcome == "trial":
            state = "trial"
            next_billing_date = trial_end_date or (start_date + timedelta(days=14))
            bm["active_subscription_count"] += 1

        elif outcome == "active":
            state = "active"
            bm["active_subscription_count"] += 1
            if selected_plan["billing_interval"] == "year":
                next_billing_date = start_date + timedelta(days=365)
            else:
                months_elapsed = max(1, (ANCHOR_DATE - start_date).days // 30)
                next_billing_date = start_date + timedelta(days=months_elapsed * 30)

        elif outcome == "paused":
            state = "paused"
            paused_date = random_date(start_date + timedelta(days=20), ANCHOR_DATE - timedelta(days=2))
            next_billing_date = paused_date + timedelta(days=25)

        elif outcome == "past_due":
            state = "past_due"
            next_billing_date = random_date(ANCHOR_DATE - timedelta(days=18), ANCHOR_DATE - timedelta(days=2))

        elif outcome == "cancelled":
            state = "cancelled"
            churn_label = 1
            bm["is_churned"] = 1
            churn_obj = weighted_choice(CHURN_REASONS, [r[2] for r in CHURN_REASONS])
            churn_code = churn_obj[0]
            bm["churn_reason"] = churn_obj[1]
            end_date = random_date(start_date + timedelta(days=20), ANCHOR_DATE - timedelta(days=5))
            next_billing_date = end_date
            cancellation_notes = f"Customer offboarded due to {churn_obj[1]}."

        # Add-on lines
        has_addons = random.random() < 0.40
        num_addons = random.randint(1, 2) if has_addons else 0
        addons_total = 0.0

        for a_idx in range(num_addons):
            addon = random.choice(ADDON_PRODUCTS)
            qty = float(random.randint(1, 5))
            subtotal = qty * addon["price"]
            addons_total += subtotal
            sub_lines.append({
                "subscription_ref": sub_ref,
                "product_name": addon["name"],
                "quantity": qty,
                "unit_price": addon["price"],
                "subtotal": subtotal,
                "is_synthetic": True
            })

        recurring_total = selected_plan["price"] + addons_total
        mrr = (recurring_total if selected_plan["billing_interval"] == "month" 
               else recurring_total / 12.0)
        arr = mrr * 12.0

        subscriptions.append({
            "name": sub_ref,
            "customer_id": cust_id,
            "customer_name": cust["name"],
            "plan_code": selected_plan["id"],
            "plan_name": selected_plan["name"],
            "state": state,
            "start_date": start_date.isoformat(),
            "trial_end_date": trial_end_date.isoformat() if trial_end_date else "",
            "next_billing_date": next_billing_date.isoformat() if next_billing_date else "",
            "end_date": end_date.isoformat() if end_date else "",
            "paused_date": paused_date.isoformat() if paused_date else "",
            "auto_renew": state not in ("cancelled", "closed"),
            "recurring_total": round(recurring_total, 2),
            "mrr": round(mrr, 2),
            "arr": round(arr, 2),
            "has_upgrade": has_upgrade,
            "has_downgrade": has_downgrade,
            "churn_code": churn_code,
            "cancellation_notes": cancellation_notes,
            "is_churned": churn_label,
            "is_synthetic": True
        })

        # 3. Generate Invoices & Payments for this Subscription over 12 months
        if state != "trial":
            # Simulate billing periods between start_date and min(end_date, ANCHOR_DATE)
            cutoff = end_date if end_date else ANCHOR_DATE
            curr_bill = start_date
            inv_idx = 1

            while curr_bill <= cutoff:
                inv_ref = f"INV/{curr_bill.year}/{len(invoices) + 1:06d}"
                bm["total_invoices"] += 1
                
                # Determine payment success vs failure
                # Past due and payment failure churn have higher fail probability
                if churn_code == "PAYMENT_FAILURE" and curr_bill >= (cutoff - timedelta(days=60)):
                    payment_status = "failed"
                elif state == "past_due" and curr_bill >= (ANCHOR_DATE - timedelta(days=20)):
                    payment_status = "failed"
                else:
                    payment_status = "paid" if random.random() < 0.94 else "failed"

                due_date = curr_bill + timedelta(days=selected_plan["grace_period_days"])

                invoices.append({
                    "invoice_ref": inv_ref,
                    "subscription_ref": sub_ref,
                    "customer_id": cust_id,
                    "customer_name": cust["name"],
                    "invoice_date": curr_bill.isoformat(),
                    "due_date": due_date.isoformat(),
                    "amount_total": round(recurring_total, 2),
                    "currency": "USD",
                    "payment_state": "paid" if payment_status == "paid" else "not_paid",
                    "state": "posted",
                    "is_synthetic": True
                })

                # Payment record
                pay_ref = f"PAY/{curr_bill.year}/{len(payments) + 1:06d}"
                if payment_status == "paid":
                    bm["total_invoices_paid"] += 1
                    bm["total_revenue_paid"] += recurring_total
                    payments.append({
                        "payment_ref": pay_ref,
                        "invoice_ref": inv_ref,
                        "subscription_ref": sub_ref,
                        "customer_id": cust_id,
                        "payment_date": (curr_bill + timedelta(days=random.randint(0, 3))).isoformat(),
                        "amount": round(recurring_total, 2),
                        "status": "successful",
                        "payment_method": random.choice(["credit_card_stripe", "ach_direct_debit", "bank_transfer"]),
                        "failure_reason": "",
                        "is_synthetic": True
                    })
                else:
                    bm["total_invoices_failed"] += 1
                    payments.append({
                        "payment_ref": pay_ref,
                        "invoice_ref": inv_ref,
                        "subscription_ref": sub_ref,
                        "customer_id": cust_id,
                        "payment_date": (curr_bill + timedelta(days=1)).isoformat(),
                        "amount": round(recurring_total, 2),
                        "status": "failed",
                        "payment_method": "credit_card_stripe",
                        "failure_reason": random.choice(PAYMENT_FAILURE_REASONS),
                        "is_synthetic": True
                    })

                # Step forward
                if selected_plan["billing_interval"] == "year":
                    curr_bill += timedelta(days=365)
                else:
                    curr_bill += timedelta(days=30 * selected_plan["billing_interval_count"])
                inv_idx += 1

    # Finalize Behavior Metrics Table
    metrics_list = []
    for cid, m in behavior_metrics.items():
        inv_total = m["total_invoices"]
        m["payment_failure_rate"] = (round(m["total_invoices_failed"] / inv_total, 3) if inv_total > 0 else 0.0)
        m["total_revenue_paid"] = round(m["total_revenue_paid"], 2)
        m["is_synthetic"] = True
        metrics_list.append(m)

    # --- Write Datasets to CSV and JSON ---
    def save_csv(filename, data, fieldnames):
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f" [CREATED] {filename}: {len(data)} records")

    # 1. Customers
    save_csv("customers.csv", customers, list(customers[0].keys()))

    # 2. Plans
    save_csv("plans.csv", PLANS, list(PLANS[0].keys()))

    # 3. Subscriptions
    save_csv("subscriptions.csv", subscriptions, list(subscriptions[0].keys()))

    # 4. Subscription Lines
    save_csv("subscription_lines.csv", sub_lines, list(sub_lines[0].keys()))

    # 5. Invoices
    save_csv("invoices.csv", invoices, list(invoices[0].keys()))

    # 6. Payments
    save_csv("payments.csv", payments, list(payments[0].keys()))

    # 7. Customer Behavioral Metrics (ML Churn Table)
    save_csv("customer_behavior_metrics.csv", metrics_list, list(metrics_list[0].keys()))

    # 8. Unified JSON payload for Odoo Loader
    json_path = os.path.join(OUTPUT_DIR, "brightloop_synthetic_dataset.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "anchor_date": ANCHOR_DATE.isoformat(),
                "random_seed": SEED,
                "is_synthetic": True,
                "disclaimer": "All customer records, transactions, and churn outcomes are synthetically generated for testing and benchmark development; ML metrics derived from this dataset do not represent production performance."
            },
            "plans": PLANS,
            "customers": customers,
            "subscriptions": subscriptions,
            "subscription_lines": sub_lines,
            "invoices": invoices,
            "payments": payments,
            "behavior_metrics": metrics_list
        }, f, indent=2)
    print(f" [CREATED] brightloop_synthetic_dataset.json: Unified dataset created successfully.")

    print("\n--- Synthetic Dataset Summary Statistics ---")
    print(f"Customers: {len(customers)}")
    print(f"Plans: {len(PLANS)}")
    print(f"Subscriptions: {len(subscriptions)}")
    state_counts = {}
    for s in subscriptions:
        state_counts[s["state"]] = state_counts.get(s["state"], 0) + 1
    print(f"Subscription States: {state_counts}")
    print(f"Subscription Lines (Add-ons): {len(sub_lines)}")
    print(f"Invoices Generated (12 Months): {len(invoices)}")
    print(f"Payment Transactions: {len(payments)}")
    fail_pays = [p for p in payments if p["status"] == "failed"]
    print(f"Payment Success / Failure: {len(payments) - len(fail_pays)} Paid / {len(fail_pays)} Failed ({len(fail_pays)/len(payments)*100:.1f}%)")
    churned_customers = [m for m in metrics_list if m["is_churned"] == 1]
    print(f"Customer Churn Rate: {len(churned_customers)} / {len(metrics_list)} ({len(churned_customers)/len(metrics_list)*100:.1f}%)")

if __name__ == "__main__":
    generate()
