# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    subscription_ids = fields.One2many(
        comodel_name='brightloop.subscription',
        inverse_name='partner_id',
        string='Subscriptions'
    )
    subscription_count = fields.Integer(
        string='Total Subscriptions',
        compute='_compute_subscription_count'
    )
    active_subscription_count = fields.Integer(
        string='Active Subscriptions',
        compute='_compute_subscription_count'
    )
    subscription_segment = fields.Selection(
        selection=[
            ('vip', 'VIP Enterprise'),
            ('growth', 'Growth Scale'),
            ('starter', 'Standard Starter'),
            ('at_risk', 'At-Risk Delinquent'),
            ('churned', 'Former Subscriber'),
            ('none', 'Non-Subscriber'),
        ],
        string='Customer Segment',
        compute='_compute_subscription_segment',
        store=True,
        help="Automated behavioral segmentation based on contract value and status."
    )
    lifetime_subscription_revenue = fields.Monetary(
        string='Subscription LTV',
        currency_field='currency_id',
        compute='_compute_subscription_ltv',
        store=True,
        help="Cumulative historical revenue generated from subscription billing."
    )
    total_arr_at_risk = fields.Monetary(
        string='Total ARR at Risk',
        currency_field='currency_id',
        compute='_compute_partner_ai_metrics',
        store=True,
        help="Aggregated annual recurring revenue at risk across all subscriptions."
    )
    customer_lifecycle_stage = fields.Selection(
        selection=[
            ('new', 'New Onboarding (<90d)'),
            ('regular', 'Steady Established (90d-365d)'),
            ('long_term', 'Long-term Champion (>365d)'),
            ('at_risk', 'At-Risk Delinquent'),
            ('churned', 'Former Churned'),
            ('none', 'Prospect / Non-Subscriber'),
        ],
        string='Customer Lifecycle Stage',
        compute='_compute_partner_ai_metrics',
        store=True,
        help="Tenure and behavioral stage classification."
    )

    @api.depends('subscription_ids', 'subscription_ids.state')
    def _compute_subscription_count(self):
        for partner in self:
            partner.subscription_count = len(partner.subscription_ids)
            partner.active_subscription_count = len(partner.subscription_ids.filtered(lambda s: s.state == 'active'))

    @api.depends('subscription_ids.invoice_ids.payment_state', 'subscription_ids.invoice_ids.amount_total')
    def _compute_subscription_ltv(self):
        for partner in self:
            total_ltv = 0.0
            for sub in partner.subscription_ids:
                paid_invoices = sub.invoice_ids.filtered(lambda inv: inv.payment_state in ('paid', 'in_payment'))
                total_ltv += sum(paid_invoices.mapped('amount_total'))
            partner.lifetime_subscription_revenue = total_ltv

    @api.depends('subscription_ids.state', 'subscription_ids.recurring_total', 'active_subscription_count')
    def _compute_subscription_segment(self):
        for partner in self:
            subs = partner.subscription_ids
            if not subs:
                partner.subscription_segment = 'none'
                continue

            active_subs = subs.filtered(lambda s: s.state == 'active')
            past_due_subs = subs.filtered(lambda s: s.state == 'past_due')

            if past_due_subs:
                partner.subscription_segment = 'at_risk'
            elif active_subs:
                max_price = max(active_subs.mapped('recurring_total'))
                if max_price >= 500.0:
                    partner.subscription_segment = 'vip'
                elif max_price >= 90.0:
                    partner.subscription_segment = 'growth'
                else:
                    partner.subscription_segment = 'starter'
            elif all(s.state in ('cancelled', 'closed') for s in subs):
                partner.subscription_segment = 'churned'
            else:
                partner.subscription_segment = 'starter'

    @api.depends('subscription_ids.predicted_loss_arr', 'subscription_ids.churn_risk_level', 'subscription_ids.state', 'subscription_ids.start_date')
    def _compute_partner_ai_metrics(self):
        today = fields.Date.context_today(self)
        for partner in self:
            subs = partner.subscription_ids
            if not subs:
                partner.total_arr_at_risk = 0.0
                partner.customer_lifecycle_stage = 'none'
                continue

            active_or_risk_subs = subs.filtered(lambda s: s.state in ('active', 'past_due', 'paused'))
            partner.total_arr_at_risk = sum(active_or_risk_subs.mapped('predicted_loss_arr'))

            if not active_or_risk_subs:
                partner.customer_lifecycle_stage = 'churned'
            elif any(s.churn_risk_level == 'high' or s.state == 'past_due' for s in active_or_risk_subs):
                partner.customer_lifecycle_stage = 'at_risk'
            else:
                valid_starts = [s.start_date for s in active_or_risk_subs if s.start_date]
                if valid_starts:
                    earliest_start = min(valid_starts)
                    days_active = (today - earliest_start).days
                    if days_active < 90:
                        partner.customer_lifecycle_stage = 'new'
                    elif days_active > 365:
                        partner.customer_lifecycle_stage = 'long_term'
                    else:
                        partner.customer_lifecycle_stage = 'regular'
                else:
                    partner.customer_lifecycle_stage = 'regular'

    def action_view_subscriptions(self):
        self.ensure_one()
        return {
            'name': _('Subscriptions - %s', self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'brightloop.subscription',
            'view_mode': 'tree,kanban,form,pivot,graph',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
