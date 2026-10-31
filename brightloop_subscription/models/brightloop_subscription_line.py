# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BrightloopSubscriptionLine(models.Model):
    _name = 'brightloop.subscription.line'
    _description = 'Brightloop Subscription Line / Add-on'
    _order = 'subscription_id, id'

    subscription_id = fields.Many2one(
        comodel_name='brightloop.subscription',
        string='Subscription',
        required=True,
        ondelete='cascade',
        index=True
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product / Add-on',
        required=True,
        domain=[('type', '=', 'service')]
    )
    name = fields.Text(
        string='Description',
        required=True
    )
    quantity = fields.Float(
        string='Quantity / Seats',
        default=1.0,
        required=True
    )
    unit_price = fields.Monetary(
        string='Unit Price',
        currency_field='currency_id',
        required=True,
        default=0.0
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='subscription_id.currency_id',
        store=True,
        readonly=True
    )
    subtotal = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_subtotal',
        store=True
    )

    _sql_constraints = [
        ('quantity_positive', 'CHECK(quantity > 0)', 'The line quantity must be strictly greater than zero!'),
        ('price_non_negative', 'CHECK(unit_price >= 0)', 'The line unit price cannot be negative!'),
    ]

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.quantity or 0.0) * (line.unit_price or 0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale() if hasattr(self.product_id, 'get_product_multiline_description_sale') else (self.product_id.name or '')
            self.unit_price = self.product_id.list_price
