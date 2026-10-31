# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BrightloopChangePlanWizard(models.TransientModel):
    _name = 'brightloop.subscription.change.plan.wizard'
    _description = 'Subscription Upgrade / Downgrade Wizard'

    subscription_id = fields.Many2one(
        comodel_name='brightloop.subscription',
        string='Subscription',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    current_plan_id = fields.Many2one(
        comodel_name='brightloop.plan',
        string='Current Plan',
        related='subscription_id.plan_id',
        readonly=True
    )
    current_price = fields.Monetary(
        string='Current Plan Price',
        currency_field='currency_id',
        related='current_plan_id.price',
        readonly=True
    )
    new_plan_id = fields.Many2one(
        comodel_name='brightloop.plan',
        string='New Subscription Plan',
        required=True
    )
    new_price = fields.Monetary(
        string='New Plan Price',
        currency_field='currency_id',
        related='new_plan_id.price',
        readonly=True
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='subscription_id.currency_id',
        readonly=True
    )
    change_type = fields.Selection(
        selection=[
            ('upgrade', 'Plan Upgrade'),
            ('downgrade', 'Plan Downgrade'),
            ('lateral', 'Plan Switch'),
        ],
        string='Change Classification',
        compute='_compute_change_type'
    )
    apply_immediately = fields.Boolean(
        string='Apply Immediately with Prorated Adjustment',
        default=True,
        help="If checked, upgrades or downgrades take effect today and prorate remaining days."
    )
    estimated_proration = fields.Monetary(
        string='Estimated Net Proration Due',
        currency_field='currency_id',
        compute='_compute_proration',
        help="Net adjustment: (New Plan Proration - Unused Balance on Current Plan)."
    )

    @api.depends('current_plan_id', 'new_plan_id')
    def _compute_change_type(self):
        for wiz in self:
            if not wiz.new_plan_id or not wiz.current_plan_id:
                wiz.change_type = 'lateral'
            elif wiz.new_plan_id.price > wiz.current_plan_id.price:
                wiz.change_type = 'upgrade'
            elif wiz.new_plan_id.price < wiz.current_plan_id.price:
                wiz.change_type = 'downgrade'
            else:
                wiz.change_type = 'lateral'

    @api.depends('subscription_id', 'new_plan_id', 'apply_immediately')
    def _compute_proration(self):
        for wiz in self:
            sub = wiz.subscription_id
            if not wiz.apply_immediately or not wiz.new_plan_id or not sub.next_billing_date:
                wiz.estimated_proration = 0.0
                continue

            today = fields.Date.context_today(wiz)
            delta = sub._get_cadence_delta()
            cycle_start = sub.next_billing_date - delta
            total_cycle_days = max(1, (sub.next_billing_date - cycle_start).days)
            remaining_days = max(0, (sub.next_billing_date - today).days)

            ratio = float(remaining_days) / float(total_cycle_days)
            unused_old = wiz.current_price * ratio
            new_charge = wiz.new_price * ratio
            wiz.estimated_proration = round(new_charge - unused_old, 2)

    def action_confirm_change_plan(self):
        """Execute plan modification on subscription."""
        self.ensure_one()
        if not self.subscription_id:
            raise UserError(_("No subscription found."))
        self.subscription_id.action_change_plan(self.new_plan_id, apply_now=self.apply_immediately)
        return {'type': 'ir.actions.act_window_close'}
