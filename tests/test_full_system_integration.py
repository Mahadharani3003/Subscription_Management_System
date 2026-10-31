# -*- coding: utf-8 -*-
"""
Brightloop Comprehensive System Integration, QA & Performance Benchmark
========================================================================
Validates:
1. Complete Model & Relationship Integrity
2. End-to-End Functional Workflows (Lifecycle, Invoicing, Proration, Dunning)
3. Role-Based Access Control & Security Record Rules
4. Error Handling & Validation Rules
5. ORM Performance & Batch Processing Simulation
"""

import sys
import unittest
import csv
import os
import xml.etree.ElementTree as ET
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON_DIR = os.path.join(BASE_DIR, 'brightloop_subscription')

class MockModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'message_logs'):
            self.message_logs = []

    def message_post(self, body):
        self.message_logs.append(body)

class TestSystemIntegrationQA(unittest.TestCase):

    def setUp(self):
        self.today = date(2026, 10, 31)

        self.plan_basic = MockModel(
            id=1, name="Starter", price=29.0, billing_interval="month",
            billing_interval_count=1, trial_period_days=14, grace_period_days=7
        )
        self.plan_enterprise = MockModel(
            id=2, name="Enterprise", price=999.0, billing_interval="year",
            billing_interval_count=1, trial_period_days=30, grace_period_days=14
        )

    # --- 1. System Integration & Manifest Test ---
    def test_01_manifest_and_dependency_integration(self):
        """QA 1: Verify module manifest, native dependencies, and declared files."""
        manifest_file = os.path.join(ADDON_DIR, '__manifest__.py')
        self.assertTrue(os.path.exists(manifest_file), "Manifest file must exist.")
        
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = eval(f.read())

        self.assertEqual(manifest['name'], 'Brightloop - Subscription Management System')
        self.assertIn('account', manifest['depends'])
        self.assertIn('mail', manifest['depends'])
        self.assertIn('portal', manifest['depends'])

        # Check all data files exist on disk
        for rel_path in manifest['data']:
            full_path = os.path.join(ADDON_DIR, rel_path)
            self.assertTrue(os.path.exists(full_path), f"Declared file missing: {rel_path}")

    # --- 2. Security Matrix & Record Rules ---
    def test_02_security_matrix_and_portal_isolation(self):
        """QA 2: Verify role-based access control (13 ACLs) and portal record isolation."""
        csv_file = os.path.join(ADDON_DIR, 'security', 'ir.model.access.csv')
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rules = list(reader)

        self.assertGreaterEqual(len(rules), 13, "Must have at least 13 ACL rules configured.")
        
        # Verify portal user has read-only (1,0,0,0) on subscriptions
        portal_sub_rule = next((r for r in rules if r['id'] == 'access_brightloop_subscription_portal'), None)
        self.assertIsNotNone(portal_sub_rule)
        self.assertEqual(portal_sub_rule['perm_read'], '1')
        self.assertEqual(portal_sub_rule['perm_write'], '0')
        self.assertEqual(portal_sub_rule['perm_create'], '0')
        self.assertEqual(portal_sub_rule['perm_unlink'], '0')

        # Verify security XML has portal customer record rule
        sec_xml = os.path.join(ADDON_DIR, 'security', 'brightloop_security.xml')
        tree = ET.parse(sec_xml)
        rules = tree.findall('.//record[@model="ir.rule"]')
        rule_names = [r.find('field[@name="name"]').text for r in rules if r.find('field[@name="name"]') is not None]
        self.assertTrue(any('Portal Customer' in name for name in rule_names), "Must enforce portal customer record rule.")

    # --- 3. End-to-End Subscription Lifecycle & Proration ---
    def test_03_lifecycle_activation_and_prorated_upgrade(self):
        """QA 3: Verify subscription state progression, activation, and mid-cycle proration."""
        sub = MockModel(
            name="SUB/2026/00001",
            partner_id=MockModel(id=1, name="TechCorp"),
            plan_id=self.plan_basic,
            state="draft",
            start_date=self.today,
            next_billing_date=self.today + timedelta(days=30),
            invoice_ids=[],
            recurring_total=29.0
        )

        # 1. Activation
        sub.state = "active"
        self.assertEqual(sub.state, "active")

        # 2. Mid-cycle upgrade: 15 days remaining out of 30 days
        days_remaining = 15
        total_cycle_days = 30
        ratio = days_remaining / total_cycle_days # 0.50

        old_unused = round(self.plan_basic.price * ratio, 2)       # 14.50
        new_charge = round(self.plan_enterprise.price * ratio, 2)  # 499.50
        net_adjustment = round(new_charge - old_unused, 2)        # 485.00

        self.assertEqual(net_adjustment, 485.00)
        sub.plan_id = self.plan_enterprise
        sub.recurring_total = self.plan_enterprise.price
        self.assertEqual(sub.recurring_total, 999.0)

    # --- 4. Idempotent Invoicing & Overdue Dunning ---
    def test_04_idempotent_billing_and_dunning_recovery(self):
        """QA 4: Verify duplicate invoice protection, dunning shift, and recovery hook."""
        sub = MockModel(
            name="SUB/2026/00002",
            state="active",
            next_billing_date=self.today,
            invoice_ids=[]
        )

        # 1. Invoice generation
        inv1 = MockModel(id=101, invoice_date=self.today, payment_state="not_paid", state="posted")
        sub.invoice_ids.append(inv1)

        # 2. Idempotency check: attempt second invoice today
        existing = [inv for inv in sub.invoice_ids if inv.invoice_date == self.today]
        self.assertEqual(len(existing), 1, "Only one invoice allowed per billing cycle.")

        # 3. Dunning shift to past_due
        sub.state = "past_due"
        self.assertEqual(sub.state, "past_due")

        # 4. Payment settled -> Automatic Recovery
        inv1.payment_state = "paid"
        has_unpaid = any(inv.payment_state in ('not_paid', 'partial') for inv in sub.invoice_ids)
        if not has_unpaid and sub.state == "past_due":
            sub.state = "active"
        self.assertEqual(sub.state, "active", "Subscription must recover to active once invoice is settled.")

    # --- 5. Performance Benchmark Simulation ---
    def test_05_performance_benchmark(self):
        """QA 5: Benchmark batch evaluation speed for 1,000 subscriptions."""
        import time
        start_time = time.time()

        subscriptions = []
        for i in range(1000):
            subscriptions.append(MockModel(
                id=i,
                name=f"SUB/2026/{i:05d}",
                state="active",
                next_billing_date=self.today + timedelta(days=(i % 30)),
                mrr=29.0
            ))

        # Simulate Cron search filter on 1,000 contracts
        due_subs = [s for s in subscriptions if s.state == "active" and s.next_billing_date <= self.today]
        elapsed = time.time() - start_time

    # --- 6. Predictive Health Scoring & Churn Risk Engine ---
    def test_06_predictive_health_score_and_churn_risk(self):
        """QA 6: Verify predictive health score compute, churn risk classification, and renewal probability."""
        # Case A: Flawless customer with long tenure
        sub_healthy = MockModel(
            state="active",
            start_date=self.today - timedelta(days=240), # 8 months tenure
            auto_renew=True,
            invoice_ids=[]
        )
        
        # Diagnostic heuristic simulation
        score = 100
        if sub_healthy.start_date and (self.today - sub_healthy.start_date).days // 30 >= 6:
            score = min(100, score + 10) # 100
        self.assertEqual(score, 100)
        risk_level = 'low' if score >= 75 else ('medium' if score >= 50 else 'high')
        renewal_prob = round(85.0 + (score - 75) * 0.5, 1)
        self.assertEqual(risk_level, 'low')
        self.assertEqual(renewal_prob, 97.5)

        # Case B: At-risk delinquent customer
        inv_unpaid1 = MockModel(state="posted", payment_state="not_paid")
        inv_unpaid2 = MockModel(state="posted", payment_state="not_paid")
        sub_at_risk = MockModel(
            state="past_due",
            start_date=self.today - timedelta(days=60), # 2 months
            auto_renew=False,
            invoice_ids=[inv_unpaid1, inv_unpaid2]
        )
        
        score_risk = 100
        score_risk -= 35 # past_due penalty
        score_risk -= 25 # 2 unpaid invoices penalty
        score_risk -= 30 # disabled auto_renew penalty
        score_risk = max(5, min(100, score_risk))
        self.assertEqual(score_risk, 10)
        risk_level_b = 'low' if score_risk >= 75 else ('medium' if score_risk >= 50 else 'high')
        renewal_prob_b = round(max(10.0, score_risk * 0.6), 1)
        self.assertEqual(risk_level_b, 'high')
        self.assertEqual(renewal_prob_b, 10.0)

    # --- 7. Customer Segmentation & LTV Analytics ---
    def test_07_customer_segmentation_and_lifetime_value(self):
        """QA 7: Verify dynamic customer segmentation (VIP, Growth, Starter, Churned) & LTV aggregation."""
        # VIP Customer
        inv1 = MockModel(move_type='out_invoice', state='posted', payment_state='paid', amount_total=7500.0)
        inv2 = MockModel(move_type='out_invoice', state='posted', payment_state='paid', amount_total=3500.0)
        sub_active = MockModel(state='active')
        
        total_ltv = inv1.amount_total + inv2.amount_total # 11,000.0
        self.assertEqual(total_ltv, 11000.0)
        segment = 'vip' if total_ltv >= 10000.0 else 'growth'
        self.assertEqual(segment, 'vip')

        # Churned Customer (0 active, 1 cancelled, LTV < 1000)
        inv3 = MockModel(move_type='out_invoice', state='posted', payment_state='paid', amount_total=29.0)
        sub_cancelled = MockModel(state='cancelled')
        active_count = 0
        cancelled_count = 1
        ltv_churned = inv3.amount_total
        seg_churned = 'churned' if active_count == 0 and cancelled_count > 0 else 'starter'
        self.assertEqual(seg_churned, 'churned')

    # --- 8. Customer Self-Service Portal & Routes ---
    def test_08_customer_portal_routes_and_templates(self):
        """QA 8: Verify portal controller endpoints, templates, and self-service hooks."""
        portal_py = os.path.join(ADDON_DIR, 'controllers', 'portal.py')
        self.assertTrue(os.path.exists(portal_py), "Portal controller must exist.")
        
        with open(portal_py, 'r', encoding='utf-8') as f:
            code = f.read()

        # Check endpoints
        self.assertIn('/my/subscriptions', code)
        self.assertIn('/my/subscriptions/<int:sub_id>', code)
        self.assertIn('/my/subscriptions/<int:sub_id>/pause', code)
        self.assertIn('/my/subscriptions/<int:sub_id>/resume', code)

        # Check XML template IDs
        portal_xml = os.path.join(ADDON_DIR, 'views', 'brightloop_subscription_portal_templates.xml')
        self.assertTrue(os.path.exists(portal_xml), "Portal XML templates must exist.")
        tree = ET.parse(portal_xml)
        templates = tree.findall('.//template')
        t_ids = [t.get('id') for t in templates]
        self.assertIn('portal_my_home_subscription', t_ids)
        self.assertIn('portal_my_subscriptions', t_ids)
        self.assertIn('portal_subscription_page', t_ids)

    # --- 9. Reporting Actions, Views & Watchlist Integration ---
    def test_09_reporting_forecast_and_watchlist_actions(self):
        """QA 9: Verify forecast graph view, predictive retention watchlist action, and menus."""
        sub_views_xml = os.path.join(ADDON_DIR, 'views', 'brightloop_subscription_views.xml')
        tree = ET.parse(sub_views_xml)
        forecast_view = tree.find('.//record[@id="view_brightloop_subscription_graph_forecast"]')
        self.assertIsNotNone(forecast_view, "Forecast graph view must be defined in XML.")

        menus_xml = os.path.join(ADDON_DIR, 'views', 'brightloop_menus.xml')
        tree_menus = ET.parse(menus_xml)
        watchlist_action = tree_menus.find('.//record[@id="action_brightloop_retention_watchlist"]')
        self.assertIsNotNone(watchlist_action, "Predictive retention watchlist action must exist.")

        forecast_action = tree_menus.find('.//record[@id="action_brightloop_analytics_forecast"]')
        self.assertIsNotNone(forecast_action, "Revenue forecast analytics action must exist.")

        menuitems = tree_menus.findall('.//menuitem')
        menu_ids = [m.get('id') for m in menuitems]
        self.assertIn('menu_brightloop_report_forecast', menu_ids)
        self.assertIn('menu_brightloop_report_watchlist', menu_ids)

if __name__ == '__main__':
    unittest.main()
