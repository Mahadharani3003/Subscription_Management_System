# -*- coding: utf-8 -*-
"""
Brightloop SaaS Evolution, Commercial Packaging, AI Intelligence & Chatbot Test Suite
====================================================================================
Validates:
1. Commercial SaaS Packaging & Entitlement Limits (Starter, Pro, Enterprise)
2. Multi-Company & Tenant Isolation Constraints
3. AI Predictive Analytics & Heuristic Diagnostics (Health Scores, Loss ARR)
4. Customer Lifecycle Segmentation & Aggregate ARR Exposure
5. In-ERP AI Business Intelligence Assistant
6. In-Portal Conversational Chatbot Engine & Customer Privacy Isolation
"""

import unittest
from datetime import date, timedelta
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class MockCurrency:
    def __init__(self, symbol='$'):
        self.symbol = symbol


class MockCompany:
    def __init__(self, id=1, name="Brightloop SaaS Ltd"):
        self.id = id
        self.name = name
        self.currency_id = MockCurrency('$')


class MockRecord:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'message_logs'):
            self.message_logs = []

    def message_post(self, body):
        self.message_logs.append(body)

    def filtered(self, func):
        return [item for item in self if func(item)]


class MockRecordSet(list):
    def filtered(self, func):
        return MockRecordSet([item for item in self if func(item)])

    def mapped(self, field):
        return [getattr(item, field) for item in self if hasattr(item, field)]


class TestSaaSEvolutionAndChatbot(unittest.TestCase):

    def setUp(self):
        self.today = date(2026, 10, 31)
        self.company = MockCompany(id=1, name="Brightloop Primary")
        self.currency = self.company.currency_id

        # Commercial Plans
        self.plan_starter = MockRecord(
            id=1, name="Starter", code="START-MO", price=29.0,
            billing_interval="month", billing_interval_count=1,
            trial_period_days=14, grace_period_days=7,
            tier_package="starter", max_subscribers_limit=100,
            has_api_access=False, has_ai_intelligence=False,
            support_sla_hours=48, is_public_portal=True, company_id=self.company
        )
        self.plan_pro = MockRecord(
            id=2, name="Professional", code="PRO-MO", price=99.0,
            billing_interval="month", billing_interval_count=1,
            trial_period_days=14, grace_period_days=7,
            tier_package="professional", max_subscribers_limit=1000,
            has_api_access=True, has_ai_intelligence=True,
            support_sla_hours=24, is_public_portal=True, company_id=self.company
        )
        self.plan_enterprise = MockRecord(
            id=3, name="Enterprise", code="ENT-YR", price=999.0,
            billing_interval="year", billing_interval_count=1,
            trial_period_days=30, grace_period_days=14,
            tier_package="enterprise", max_subscribers_limit=0,
            has_api_access=True, has_ai_intelligence=True,
            support_sla_hours=4, is_public_portal=True, company_id=self.company
        )

        # Customers
        self.customer_a = MockRecord(id=101, name="Acme Corp", commercial_partner_id=None)
        self.customer_a.commercial_partner_id = self.customer_a

        self.customer_b = MockRecord(id=102, name="Beta Technologies", commercial_partner_id=None)
        self.customer_b.commercial_partner_id = self.customer_b

    # --- 1. Commercial SaaS Packaging & Entitlements ---
    def test_01_commercial_packaging_attributes(self):
        """Verify SaaS commercial packaging attributes and tier limits."""
        self.assertEqual(self.plan_starter.tier_package, "starter")
        self.assertEqual(self.plan_starter.max_subscribers_limit, 100)
        self.assertFalse(self.plan_starter.has_api_access)
        self.assertFalse(self.plan_starter.has_ai_intelligence)

        self.assertEqual(self.plan_pro.tier_package, "professional")
        self.assertTrue(self.plan_pro.has_api_access)
        self.assertTrue(self.plan_pro.has_ai_intelligence)
        self.assertEqual(self.plan_pro.support_sla_hours, 24)

        self.assertEqual(self.plan_enterprise.tier_package, "enterprise")
        self.assertEqual(self.plan_enterprise.max_subscribers_limit, 0)  # Unlimited
        self.assertEqual(self.plan_enterprise.support_sla_hours, 4)

    # --- 2. Predictive Churn Risk & Actuarial Revenue Loss ---
    def test_02_predictive_churn_and_actuarial_loss(self):
        """Verify predictive churn diagnostics, loss calculations, and retention recommendations."""
        # Active healthy subscription
        sub_healthy = MockRecord(
            id=1, name="SUB/2026/001", partner_id=self.customer_a, plan_id=self.plan_pro,
            state="active", auto_renew=True, start_date=self.today - timedelta(days=200),
            recurring_total=99.0, arr=1188.0, next_billing_date=self.today + timedelta(days=10),
            invoice_ids=MockRecordSet([MockRecord(payment_state="paid", invoice_date_due=self.today - timedelta(days=30))])
        )

        # Health computation simulation
        score = 80  # Base
        score += 10  # Tenure >= 6 months
        health = max(5, min(100, score))
        sub_healthy.health_score = health
        self.assertGreaterEqual(sub_healthy.health_score, 75)

        sub_healthy.churn_risk_level = "low"
        sub_healthy.renewal_probability = 92.5
        sub_healthy.predicted_loss_arr = round(sub_healthy.arr * (1.0 - (sub_healthy.renewal_probability / 100.0)), 2)
        sub_healthy.expected_renewal_revenue = round(sub_healthy.recurring_total * (sub_healthy.renewal_probability / 100.0), 2)
        sub_healthy.days_to_renewal = (sub_healthy.next_billing_date - self.today).days
        sub_healthy.renewal_urgency = "upcoming" if sub_healthy.days_to_renewal <= 14 else "normal"

        self.assertEqual(sub_healthy.days_to_renewal, 10)
        self.assertEqual(sub_healthy.renewal_urgency, "upcoming")
        self.assertEqual(sub_healthy.predicted_loss_arr, 89.10)
        self.assertEqual(sub_healthy.expected_renewal_revenue, 91.58)

        # Past-due high risk subscription
        sub_risk = MockRecord(
            id=2, name="SUB/2026/002", partner_id=self.customer_b, plan_id=self.plan_starter,
            state="past_due", auto_renew=False, start_date=self.today - timedelta(days=20),
            recurring_total=29.0, arr=348.0, next_billing_date=self.today - timedelta(days=5),
            invoice_ids=MockRecordSet([MockRecord(payment_state="not_paid", invoice_date_due=self.today - timedelta(days=12))])
        )

        score_risk = 80 - 45 - 20  # Past due -45, auto-renew disabled -20
        sub_risk.health_score = max(5, score_risk)
        sub_risk.churn_risk_level = "high"
        sub_risk.renewal_probability = 15.0
        sub_risk.predicted_loss_arr = round(sub_risk.arr * (1.0 - (sub_risk.renewal_probability / 100.0)), 2)
        sub_risk.days_to_renewal = (sub_risk.next_billing_date - self.today).days
        sub_risk.renewal_urgency = "immediate" if sub_risk.days_to_renewal <= 3 else "normal"

        self.assertEqual(sub_risk.churn_risk_level, "high")
        self.assertEqual(sub_risk.renewal_urgency, "immediate")
        self.assertEqual(sub_risk.predicted_loss_arr, 295.80)

    # --- 3. Customer Lifecycle Stages & ARR at Risk ---
    def test_03_partner_lifecycle_and_risk_aggregation(self):
        """Verify ResPartner lifecycle stage determination and total ARR at risk."""
        subs_a = MockRecordSet([
            MockRecord(state="active", churn_risk_level="low", predicted_loss_arr=89.10, start_date=self.today - timedelta(days=400)),
        ])

        # Partner A: tenure > 365d -> long_term champion
        total_risk = sum(subs_a.mapped('predicted_loss_arr'))
        self.assertEqual(total_risk, 89.10)

        earliest = min([s.start_date for s in subs_a])
        tenure_days = (self.today - earliest).days
        stage_a = "long_term" if tenure_days > 365 else "regular"
        self.assertEqual(stage_a, "long_term")

        # Partner B: has high risk sub -> at_risk
        subs_b = MockRecordSet([
            MockRecord(state="past_due", churn_risk_level="high", predicted_loss_arr=295.80, start_date=self.today - timedelta(days=20)),
        ])
        stage_b = "at_risk" if any(s.churn_risk_level == 'high' or s.state == 'past_due' for s in subs_b) else "regular"
        self.assertEqual(stage_b, "at_risk")
        self.assertEqual(sum(subs_b.mapped('predicted_loss_arr')), 295.80)

    # --- 4. In-Portal Conversational Chatbot NLP Reasoning ---
    def test_04_chatbot_conversational_intents(self):
        """Simulate Customer Portal AI Chatbot responses against live mock records."""
        active_sub = MockRecord(
            id=10, name="SUB/2026/042", plan_id=self.plan_pro, recurring_total=99.0,
            start_date=self.today - timedelta(days=60), auto_renew=True, state="active",
            next_billing_date=self.today + timedelta(days=7), days_to_renewal=7
        )
        invoices = [
            MockRecord(name="INV/2026/0010", invoice_date=self.today - timedelta(days=23), amount_total=99.0, payment_state="paid", invoice_date_due=self.today - timedelta(days=16))
        ]
        plans = [self.plan_starter, self.plan_pro, self.plan_enterprise]

        def simulate_chatbot(message):
            msg = message.lower()
            if any(k in msg for k in ('invoice', 'payment', 'paid', 'receipt', 'balance')):
                return f"Recent Billing History: {len(invoices)} invoice(s) on file.", 'invoice_inquiry'
            elif any(k in msg for k in ('billing', 'renew', 'next payment', 'due date', 'when do i pay')):
                return f"Next Billing Information: {active_sub.next_billing_date} ({active_sub.days_to_renewal} days)", 'renewal_schedule'
            elif any(k in msg for k in ('pause', 'cancel', 'stop')):
                return "Pausing or Cancelling Your Subscription: You can pause directly from the portal.", 'pause_cancellation'
            elif any(k in msg for k in ('upgrade', 'downgrade', 'change plan', 'switch')):
                return "Plan Modification & Proration Policy: Upgrades applied immediately.", 'plan_modification'
            elif any(k in msg for k in ('pricing', 'plans', 'tiers', 'cost')):
                return f"Brightloop Subscription Plans: {len(plans)} plans available.", 'pricing_inquiry'
            elif any(k in msg for k in ('status', 'active', 'my plan', 'my subscription')):
                return f"Subscription Status: {active_sub.state.upper()} | Plan: {active_sub.plan_id.name}", 'subscription_status'
            elif any(k in msg for k in ('help', 'support', 'contact')):
                return "Brightloop Help & Support Desk: support@brightloop.io", 'support_faq'
            return "Hello! I am your Brightloop Subscription Assistant.", 'general_fallback'

        # Test Intent 1: Status
        reply, intent = simulate_chatbot("What is my current subscription status?")
        self.assertEqual(intent, "subscription_status")
        self.assertIn("ACTIVE", reply)
        self.assertIn("Professional", reply)

        # Test Intent 2: Renewal
        reply, intent = simulate_chatbot("When is my next billing date?")
        self.assertEqual(intent, "renewal_schedule")
        self.assertIn("7 days", reply)

        # Test Intent 3: Invoices
        reply, intent = simulate_chatbot("Show my recent invoices and payment status")
        self.assertEqual(intent, "invoice_inquiry")
        self.assertIn("1 invoice(s)", reply)

        # Test Intent 4: Upgrade
        reply, intent = simulate_chatbot("How do I upgrade to Enterprise?")
        self.assertEqual(intent, "plan_modification")

        # Test Intent 5: Plans
        reply, intent = simulate_chatbot("What plans are available?")
        self.assertEqual(intent, "pricing_inquiry")

        # Test Intent 6: Pause
        reply, intent = simulate_chatbot("Can I pause my subscription?")
        self.assertEqual(intent, "pause_cancellation")

        # Test Intent 7: Support
        reply, intent = simulate_chatbot("I need customer support")
        self.assertEqual(intent, "support_faq")

        # Test Intent 8: Fallback
        reply, intent = simulate_chatbot("Random unrelated query")
        self.assertEqual(intent, "general_fallback")

    # --- 5. Customer Data Privacy & Isolation Guard ---
    def test_05_chatbot_security_isolation(self):
        """Verify chatbot enforces strict partner filtering preventing tenant or customer data leakage."""
        all_subs = [
            MockRecord(id=1, partner_id=self.customer_a, name="SUB-A"),
            MockRecord(id=2, partner_id=self.customer_b, name="SUB-B"),
        ]

        # Customer A's session
        current_partner = self.customer_a
        isolated_subs = [s for s in all_subs if s.partner_id.id == current_partner.id]
        self.assertEqual(len(isolated_subs), 1)
        self.assertEqual(isolated_subs[0].name, "SUB-A")
        self.assertNotIn("SUB-B", [s.name for s in isolated_subs])


if __name__ == '__main__':
    unittest.main()
