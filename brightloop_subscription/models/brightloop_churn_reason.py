# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class BrightloopChurnReason(models.Model):
    _name = 'brightloop.churn.reason'
    _description = 'Brightloop Subscription Churn Reason'
    _order = 'sequence, name'

    name = fields.Char(
        string='Reason',
        required=True,
        translate=True,
        help="Reason why a customer cancelled or discontinued subscription."
    )
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help="Machine-readable code for analytics and integrations."
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    description = fields.Text(
        string='Description',
        help="Detailed context regarding this churn category."
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    subscription_ids = fields.One2many(
        comodel_name='brightloop.subscription',
        inverse_name='churn_reason_id',
        string='Churned Subscriptions'
    )
    subscription_count = fields.Integer(
        string='Churn Count',
        compute='_compute_subscription_count'
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The churn reason code must be unique!')
    ]

    @api.depends('subscription_ids')
    def _compute_subscription_count(self):
        for record in self:
            record.subscription_count = len(record.subscription_ids)
