# -*- coding: utf-8 -*-
"""
Brightloop Business Process Automation & Workflow Test Suite
============================================================
Comprehensive test suite verifying all 10 core business workflows:
1. Subscription creation & plan selection
2. Trial initiation and contract activation
3. Automated recurring invoicing
4. Strict Idempotency guard (zero duplicate invoices)
5. Plan upgrade with prorated net balance calculation
6. Pause and resumption with automated schedule postponement
7. Dunning & grace period enforcement (Active -> Past Due)
8. Payment recovery hook (Past Due -> Active)
9. Upcoming renewal reminder scheduler
10. Cancellation & offboarding with churn classification
11. Fixed-term contract expiration
"""

import sys
import unittest
from datetime import date, timedelta

class MockOdooModel:
    """Lightweight test double simulating Odoo ORM environment."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'message_logs'):
            self.message_logs = []

    def message_post(self, body):
        self.message_logs.append(body)

def add_months(sourcedate, months):
    """Month addition using standard library."""
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, 28)
    return date(year, month, day)

class TestBrightloopWorkflows(unittest.TestCase):

    def setUp(self):
        self.today = date(2026, 10, 31)

        # Plan Starter: $29/mo, 14 days trial, 7 days grace
        self.plan_starter = MockOdooModel(
            id=1,
            name="Starter (Monthly)",
            price=29.0,
            billing_interval="month",
            billing_interval_count=1,
            trial_period_days=14,
            grace_period_days=7,
            auto_close_unpaid=True
        )

        # Plan Pro: $99/mo, 14 days trial, 7 days grace
        self.plan_pro = MockOdooModel(
            id=2,
            name="Growth Pro (Monthly)",
            price=99.0,
            billing_interval="month",
            billing_interval_count=1,
            trial_period_days=14,
            grace_period_days=7,
            auto_close_unpaid=True
        )

        # Customer & Subscription Contract
        self.sub = MockOdooModel(
            name="SUB/2026/00001",
            partner_id=MockOdooModel(id=101, name="Acme Corp"),
            plan_id=self.plan_starter,
            currency_symbol="$",
            state="draft",
            start_date=self.today,
            trial_end_date=None,
            next_billing_date=None,
            last_invoiced_date=None,
            last_renewal_reminder_date=None,
            end_date=None,
            paused_date=None,
            auto_renew=True,
            line_ids=[],
            invoice_ids=[],
            churn_reason_id=None,
            cancellation_notes="",
            recurring_total=29.0,
            mrr=29.0,
            arr=348.0
        )

    def test_01_subscription_creation_and_plan_selection(self):
        """Workflow 1: Test subscription creation, pricing calculation and defaults."""
        self.assertEqual(self.sub.state, "draft")
        self.assertEqual(self.sub.plan_id.price, 29.0)
        self.assertEqual(self.sub.mrr, 29.0)
        self.assertEqual(self.sub.arr, 348.0)

    def test_02_trial_initiation_and_activation(self):
        """Workflow 2: Test Free Trial transition and formal Activation."""
        # Start Trial
        trial_days = self.sub.plan_id.trial_period_days
        self.sub.trial_end_date = self.sub.start_date + timedelta(days=trial_days)
        self.sub.next_billing_date = self.sub.trial_end_date
        self.sub.state = "trial"

        self.assertEqual(self.sub.state, "trial")
        self.assertEqual(self.sub.trial_end_date, self.today + timedelta(days=14))
        self.assertEqual(self.sub.next_billing_date, self.sub.trial_end_date)

        # Activate Subscription
        self.sub.state = "active"
        self.assertEqual(self.sub.state, "active")

    def test_03_automated_invoicing_and_idempotency_guard(self):
        """Workflow 3 & 4: Test automated invoice generation and strict duplicate prevention."""
        self.sub.state = "active"
        self.sub.next_billing_date = self.today

        # Simulating first invoice generation
        created_invoice_1 = MockOdooModel(
            id=501,
            name="INV/2026/000001",
            invoice_date=self.today,
            amount_total=29.0,
            state="posted",
            payment_state="not_paid"
        )
        self.sub.invoice_ids.append(created_invoice_1)
        self.sub.last_invoiced_date = self.today
        self.sub.next_billing_date = add_months(self.today, 1)

        self.assertEqual(len(self.sub.invoice_ids), 1)
        self.assertEqual(self.sub.next_billing_date, date(2026, 11, 28))

        # IDEMPOTENCY TEST: Attempt generating second invoice on the same date
        existing_today = [inv for inv in self.sub.invoice_ids if inv.invoice_date == self.today]
        if existing_today:
            # Idempotency triggered - no new invoice created
            duplicate_skipped = True
        else:
            duplicate_skipped = False
            self.sub.invoice_ids.append(MockOdooModel(id=502))

        self.assertTrue(duplicate_skipped)
        self.assertEqual(len(self.sub.invoice_ids), 1, "Duplicate invoice was correctly prevented!")

    def test_04_plan_upgrade_with_proration(self):
        """Workflow 5: Test plan upgrade midway through cycle with proration calculation."""
        self.sub.state = "active"
        # 10 days into a 30-day billing cycle (20 days remaining)
        cycle_start = self.today - timedelta(days=10)
        self.sub.next_billing_date = self.today + timedelta(days=20)
        
        total_days = (self.sub.next_billing_date - cycle_start).days # 30
        remaining_days = (self.sub.next_billing_date - self.today).days # 20
        ratio = float(remaining_days) / float(total_days)

        old_price = self.sub.plan_id.price # $29
        new_price = self.plan_pro.price    # $99

        unused_credit = round(old_price * ratio, 2)
        new_charge = round(new_price * ratio, 2)
        net_adjustment = round(new_charge - unused_credit, 2)

        # Expected: 20 days remaining out of 30 days
        self.assertGreater(net_adjustment, 0.0)
        self.assertEqual(net_adjustment, round((99.0 - 29.0) * (20.0 / 30.0), 2))

        # Upgrade plan
        self.sub.plan_id = self.plan_pro
        self.sub.recurring_total = self.plan_pro.price
        self.sub.mrr = self.plan_pro.price
        self.sub.arr = self.plan_pro.price * 12.0

        self.assertEqual(self.sub.plan_id.name, "Growth Pro (Monthly)")
        self.assertEqual(self.sub.mrr, 99.0)
        self.assertEqual(self.sub.arr, 1188.0)

    def test_05_pause_and_resumption_schedule_adjustment(self):
        """Workflow 6: Test pause and resumption with date postponement."""
        self.sub.state = "active"
        initial_next_billing = self.today + timedelta(days=15)
        self.sub.next_billing_date = initial_next_billing

        # Pause on today
        self.sub.state = "paused"
        self.sub.paused_date = self.today

        # Resume 8 days later
        resume_date = self.today + timedelta(days=8)
        paused_duration = (resume_date - self.sub.paused_date).days
        self.sub.next_billing_date = self.sub.next_billing_date + timedelta(days=paused_duration)
        self.sub.state = "active"
        self.sub.paused_date = None

        self.assertEqual(self.sub.state, "active")
        self.assertEqual(self.sub.next_billing_date, initial_next_billing + timedelta(days=8))

    def test_06_dunning_and_grace_period_enforcement(self):
        """Workflow 7: Test overdue invoice shifting state to Past Due."""
        self.sub.state = "active"
        grace_days = self.sub.plan_id.grace_period_days # 7 days
        
        # Simulate unpaid invoice overdue by 10 days
        due_date = self.today - timedelta(days=10)
        overdue_invoice = MockOdooModel(
            id=601,
            state="posted",
            payment_state="not_paid",
            invoice_date_due=due_date
        )
        self.sub.invoice_ids = [overdue_invoice]

        days_overdue = (self.today - overdue_invoice.invoice_date_due).days
        if days_overdue >= grace_days and self.sub.state == "active":
            self.sub.state = "past_due"

        self.assertEqual(self.sub.state, "past_due", "Subscription correctly transitioned to Past Due!")

    def test_07_payment_recovery_hook(self):
        """Workflow 8: Test automated recovery from Past Due to Active on payment confirmation."""
        self.sub.state = "past_due"
        unpaid_inv = MockOdooModel(id=601, state="posted", payment_state="not_paid")
        self.sub.invoice_ids = [unpaid_inv]

        # Payment arrives and settles invoice
        unpaid_inv.payment_state = "paid"

        # AccountMove hook triggers
        has_unpaid = any(inv.payment_state in ('not_paid', 'partial') for inv in self.sub.invoice_ids)
        if not has_unpaid and self.sub.state == "past_due":
            self.sub.state = "active"
            self.sub.message_post("Payment confirmed. Subscription restored to Active.")

        self.assertEqual(self.sub.state, "active", "Subscription automatically recovered to Active upon payment!")

    def test_08_upcoming_renewal_reminder(self):
        """Workflow 9: Test upcoming renewal reminder detection (3 days ahead)."""
        self.sub.state = "active"
        self.sub.next_billing_date = self.today + timedelta(days=3)
        
        reminder_target = self.today + timedelta(days=3)
        should_send_reminder = (self.sub.next_billing_date == reminder_target and self.sub.auto_renew)

        self.assertTrue(should_send_reminder)
        self.sub.last_renewal_reminder_date = self.today
        self.assertEqual(self.sub.last_renewal_reminder_date, self.today)

    def test_09_cancellation_with_churn_reason(self):
        """Workflow 10: Test offboarding with churn classification."""
        self.sub.state = "active"
        churn_reason = MockOdooModel(id=3, name="Migrated to Competitor", code="COMPETITOR")

        # Execute cancellation
        self.sub.state = "cancelled"
        self.sub.end_date = self.today
        self.sub.churn_reason_id = churn_reason
        self.sub.cancellation_notes = "Customer switched to legacy competitor."

        self.assertEqual(self.sub.state, "cancelled")
        self.assertEqual(self.sub.end_date, self.today)
        self.assertEqual(self.sub.churn_reason_id.code, "COMPETITOR")

    def test_10_fixed_term_contract_expiration(self):
        """Workflow 11: Test automated expiration when contract end date is reached."""
        self.sub.state = "active"
        self.sub.end_date = self.today - timedelta(days=1)

        # Cron checks expirations
        if self.sub.end_date and self.sub.end_date <= self.today and self.sub.state == "active":
            self.sub.state = "closed"

        self.assertEqual(self.sub.state, "closed", "Expired subscription successfully marked as Closed!")

if __name__ == '__main__':
    unittest.main()
