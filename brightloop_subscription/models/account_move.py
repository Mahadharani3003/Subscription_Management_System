# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_ids = fields.Many2many(
        comodel_name='brightloop.subscription',
        relation='brightloop_subscription_invoice_rel',
        column1='invoice_id',
        column2='subscription_id',
        string='Linked Subscriptions',
        readonly=True,
        help="Subscriptions billed by this invoice."
    )

    def write(self, vals):
        """Hook into payment state changes to automate subscription recovery and notifications."""
        previous_payment_states = {move.id: move.payment_state for move in self}
        res = super().write(vals)

        if 'payment_state' in vals:
            for move in self:
                old_state = previous_payment_states.get(move.id)
                new_state = move.payment_state
                if new_state in ('paid', 'in_payment') and old_state not in ('paid', 'in_payment'):
                    move._on_subscription_invoice_paid()

        return res

    def _on_subscription_invoice_paid(self):
        """Execute automated business recovery when subscription invoice is settled."""
        self.ensure_one()
        template = self.env.ref('brightloop_subscription.mail_template_subscription_payment_success', raise_if_not_found=False)

        for sub in self.subscription_ids:
            # 1. If subscription was in past_due, restore to active
            if sub.state == 'past_due':
                sub.state = 'active'
                sub.message_post(
                    body=_("Payment confirmed for invoice <b>%s</b>. Outstanding arrears resolved; subscription restored to <b>Active</b>.") % self.name
                )
            else:
                sub.message_post(
                    body=_("Payment of %s confirmed for recurring invoice <b>%s</b>.") % (
                        f"{self.amount_total} {self.currency_id.symbol}", self.name
                    )
                )

            # 2. Dispatch automated payment success notification
            if template:
                try:
                    template.send_mail(sub.id, force_send=True)
                except Exception as e:
                    _logger.warning("Failed to send payment confirmation email for sub %s: %s", sub.name, str(e))
