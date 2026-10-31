# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BrightloopPlan(models.Model):
    _name = 'brightloop.plan'
    _description = 'Brightloop Subscription Plan'
    _order = 'sequence, id desc'

    name = fields.Char(
        string='Plan Name',
        required=True,
        translate=True,
        help="Display name of the subscription plan (e.g. Starter, Growth, Enterprise)."
    )
    code = fields.Char(
        string='Plan Code',
        required=True,
        index=True,
        help="Unique identifier code for the plan (e.g. STARTER-MO, PRO-YR)."
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Sequence ordering for plan display."
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Recurring Product',
        required=True,
        domain=[('type', '=', 'service')],
        help="Linked service product used for invoicing and accounting."
    )
    billing_interval = fields.Selection(
        selection=[
            ('day', 'Day(s)'),
            ('month', 'Month(s)'),
            ('year', 'Year(s)'),
        ],
        string='Billing Interval Unit',
        default='month',
        required=True,
        help="Frequency cadence for recurring billing."
    )
    billing_interval_count = fields.Integer(
        string='Billing Cadence Count',
        default=1,
        required=True,
        help="Multiplier for interval (e.g. 1 Month, 3 Months, 1 Year)."
    )
    price = fields.Monetary(
        string='Recurring Price',
        currency_field='currency_id',
        required=True,
        default=0.0,
        help="Base subscription price per billing period."
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='product_id.currency_id',
        store=True,
        readonly=False,
        help="Currency for the plan."
    )
    trial_period_days = fields.Integer(
        string='Trial Period (Days)',
        default=0,
        help="Number of free trial days before the first bill is generated. Set 0 for no trial."
    )
    grace_period_days = fields.Integer(
        string='Grace Period (Days)',
        default=7,
        help="Days after due date before subscription is marked as past due or suspended."
    )
    auto_close_unpaid = fields.Boolean(
        string='Auto-Close on Failed Payment',
        default=True,
        help="If enabled, contracts with unpaid invoices past the grace period will be automatically closed."
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Set to false to archive the plan."
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help="Company associated with this plan."
    )
    description = fields.Html(
        string='Plan Description & Benefits',
        help="Public or internal summary of features included in this plan."
    )
    subscription_ids = fields.One2many(
        comodel_name='brightloop.subscription',
        inverse_name='plan_id',
        string='Subscriptions'
    )
    subscription_count = fields.Integer(
        string='Subscribers Count',
        compute='_compute_subscription_count',
        help="Total number of active or registered subscriptions on this plan."
    )

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'The Plan Code must be unique per company!'),
        ('price_positive', 'CHECK(price >= 0)', 'The plan price must be positive or zero!'),
        ('interval_count_positive', 'CHECK(billing_interval_count > 0)', 'The billing cadence count must be greater than zero!'),
        ('trial_days_positive', 'CHECK(trial_period_days >= 0)', 'Trial days must be zero or positive!'),
        ('grace_days_positive', 'CHECK(grace_period_days >= 0)', 'Grace days must be zero or positive!'),
    ]

    @api.constrains('code')
    def _check_code(self):
        for plan in self:
            if plan.code and not plan.code.strip():
                raise ValidationError(_("Plan Code cannot be empty or just whitespace."))

    @api.depends('subscription_ids')
    def _compute_subscription_count(self):
        for plan in self:
            plan.subscription_count = len(plan.subscription_ids)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.price or self.price == 0.0:
                self.price = self.product_id.list_price
            if not self.name:
                self.name = self.product_id.name

    def action_view_subscriptions(self):
        self.ensure_one()
        return {
            'name': _('Subscriptions - %s', self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'brightloop.subscription',
            'view_mode': 'tree,kanban,form,pivot,graph',
            'domain': [('plan_id', '=', self.id)],
            'context': {'default_plan_id': self.id},
        }
