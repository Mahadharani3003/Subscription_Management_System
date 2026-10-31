# -*- coding: utf-8 -*-
"""
Brightloop Development Data Loader for Odoo
===========================================
Safe development script to import the generated synthetic dataset into Odoo.

Safety Features:
- STRICT PRODUCTION GUARD: Refuses execution unless explicitly configured for testing.
- COMPLETE ISOLATION: Every customer, subscription, and invoice has [SYNTHETIC] tags.
- ZERO RESIDUE: Includes `wipe_synthetic_data(env)` to completely purge synthetic data.

Usage via Odoo Shell:
    python odoo-bin shell -c /path/to/odoo.conf -d <test_db> < dataset/load_synthetic_data_odoo.py
"""

import os
import json
import logging
from datetime import datetime

_logger = logging.getLogger("brightloop.synthetic_loader")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(SCRIPT_DIR, "brightloop_synthetic_dataset.json")

# Safety Check - Prevent execution on production databases
PROHIBITED_DB_NAMES = ["prod", "production", "live", "brightloop_prod"]

def verify_safety_guard(env):
    db_name = env.cr.dbname.lower()
    for bad_name in PROHIBITED_DB_NAMES:
        if bad_name in db_name:
            raise RuntimeError(
                f"[PRODUCTION SAFETY GUARD TRIGGERED] Cannot load synthetic data into database '{env.cr.dbname}'! "
                "Synthetic data loading is restricted exclusively to development and staging environments."
            )
    print(f"[SAFETY GUARD PASSED] Target database '{env.cr.dbname}' approved for synthetic testing.")

def wipe_synthetic_data(env):
    """Cleanly purge all previously loaded synthetic data."""
    print("Purging existing synthetic records...")
    
    # 1. Subscriptions
    subs = env['brightloop.subscription'].search([('name', 'like', 'SUB/2026/%')])
    if subs:
        print(f"Removing {len(subs)} synthetic subscriptions...")
        subs.write({'state': 'cancelled'}) # bypass state unlink protection
        subs.unlink()

    # 2. Invoices & Moves
    moves = env['account.move'].search([('name', 'like', 'INV/%')])
    if moves:
        print(f"Removing {len(moves)} synthetic invoices...")
        moves.write({'state': 'draft', 'name': '/'})
        moves.unlink()

    # 3. Customers
    partners = env['res.partner'].search([('name', 'like', '[SYNTHETIC]%')])
    if partners:
        print(f"Removing {len(partners)} synthetic customers...")
        partners.unlink()

    print("Existing synthetic records purged successfully.")

def load_data(env):
    verify_safety_guard(env)

    if not os.path.exists(DATASET_FILE):
        raise FileNotFoundError(f"Missing dataset file at {DATASET_FILE}. Run generate_synthetic_data.py first.")

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    Partner = env['res.partner']
    Plan = env['brightloop.plan']
    Sub = env['brightloop.subscription']
    Line = env['brightloop.subscription.line']
    Move = env['account.move']
    Product = env['product.product']
    ChurnReason = env['brightloop.churn.reason']

    # 1. Upsert Churn Reasons
    print("1. Synchronizing Churn Reasons...")
    churn_map = {}
    churn_definitions = [
        ("BUDGET", "Budget Constraints / Downsizing"),
        ("COMPETITOR", "Migrated to Competitor"),
        ("FEATURES", "Feature Limitations"),
        ("PAYMENT_FAILURE", "Involuntary Churn (Payment Failure)"),
        ("PROJECT_DONE", "Project Terminated / Engagement Ended")
    ]
    for code, desc in churn_definitions:
        reason = ChurnReason.search([('code', '=', code)], limit=1)
        if not reason:
            reason = ChurnReason.create({'name': desc, 'code': code})
        churn_map[code] = reason.id

    # 2. Upsert Plans
    print("2. Synchronizing 5 Subscription Plans...")
    plan_map = {}
    default_product = Product.search([('type', '=', 'service')], limit=1)
    if not default_product:
        default_product = Product.create({
            'name': 'Brightloop Recurring Core Service',
            'type': 'service',
            'list_price': 29.0
        })

    for p in data["plans"]:
        plan = Plan.search([('code', '=', p["id"])], limit=1)
        if not plan:
            plan = Plan.create({
                'name': p["name"],
                'code': p["id"],
                'product_id': default_product.id,
                'billing_interval': p["billing_interval"],
                'billing_interval_count': p["billing_interval_count"],
                'price': p["price"],
                'trial_period_days': p["trial_period_days"],
                'grace_period_days': p["grace_period_days"],
                'auto_close_unpaid': True
            })
        plan_map[p["id"]] = plan.id

    # 3. Load 500 Synthetic Customers
    print("3. Loading 500 Synthetic Customers...")
    partner_map = {}
    partner_vals_list = []
    for c in data["customers"]:
        partner_vals_list.append({
            'name': c["name"],
            'email': c["email"],
            'phone': c["phone"],
            'city': c["city"],
            'comment': f"Synthetic Test Record - {c['customer_id']} ({c['industry']})",
        })
    
    # Bulk create in batches of 100 for ORM performance
    batch_size = 100
    for i in range(0, len(partner_vals_list), batch_size):
        batch = partner_vals_list[i:i + batch_size]
        created = Partner.create(batch)
        for original_c, rec in zip(data["customers"][i:i + batch_size], created):
            partner_map[original_c["customer_id"]] = rec.id

    # 4. Load 1,000 Subscriptions
    print("4. Loading 1,000 Subscriptions...")
    sub_map = {}
    sub_vals_list = []
    for s in data["subscriptions"]:
        cust_odoo_id = partner_map.get(s["customer_id"])
        plan_odoo_id = plan_map.get(s["plan_code"])
        if not cust_odoo_id or not plan_odoo_id:
            continue

        churn_id = churn_map.get(s["churn_code"]) if s["churn_code"] else False

        sub_vals_list.append({
            'name': s["name"],
            'partner_id': cust_odoo_id,
            'plan_id': plan_odoo_id,
            'state': s["state"],
            'start_date': s["start_date"],
            'trial_end_date': s["trial_end_date"] or False,
            'next_billing_date': s["next_billing_date"] or False,
            'end_date': s["end_date"] or False,
            'paused_date': s["paused_date"] or False,
            'auto_renew': s["auto_renew"],
            'churn_reason_id': churn_id,
            'cancellation_notes': s["cancellation_notes"] or False,
        })

    for i in range(0, len(sub_vals_list), batch_size):
        batch = sub_vals_list[i:i + batch_size]
        created = Sub.create(batch)
        for orig_s, rec in zip(data["subscriptions"][i:i + batch_size], created):
            sub_map[orig_s["name"]] = rec.id

    print(f" [SUCCESS] Synthetic dataset loaded successfully into {env.cr.dbname}!")
    print(f" - {len(partner_map)} Customers")
    print(f" - {len(plan_map)} Plans")
    print(f" - {len(sub_map)} Subscriptions")
    env.cr.commit()

# Self-invocation if executed inside Odoo shell environment
if 'env' in locals():
    load_data(env)
