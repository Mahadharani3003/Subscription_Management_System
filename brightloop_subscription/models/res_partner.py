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

    @api.depends('subscription_ids', 'subscription_ids.state')
    def _compute_subscription_count(self):
        for partner in self:
            partner.subscription_count = len(partner.subscription_ids)
            partner.active_subscription_count = len(partner.subscription_ids.filtered(lambda s: s.state == 'active'))

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
