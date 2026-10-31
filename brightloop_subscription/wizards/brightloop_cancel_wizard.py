# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BrightloopCancelWizard(models.TransientModel):
    _name = 'brightloop.subscription.cancel.wizard'
    _description = 'Subscription Cancellation & Churn Wizard'

    subscription_id = fields.Many2one(
        comodel_name='brightloop.subscription',
        string='Subscription',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )
    churn_reason_id = fields.Many2one(
        comodel_name='brightloop.churn.reason',
        string='Reason for Cancellation',
        required=True,
        help="Classify the root cause of churn for analytics."
    )
    cancellation_notes = fields.Text(
        string='Customer Feedback & Notes',
        help="Document specific feedback or conditions leading to cancellation."
    )
    cancel_immediately = fields.Boolean(
        string='Cancel Immediately',
        default=True,
        help="If checked, terminates access today. Otherwise, service ends at the next billing date."
    )

    def action_confirm_cancellation(self):
        """Execute cancellation and offboarding."""
        self.ensure_one()
        if not self.subscription_id:
            raise UserError(_("No subscription found."))
        
        sub = self.subscription_id
        if self.cancel_immediately:
            sub.action_cancel(churn_reason_id=self.churn_reason_id.id, notes=self.cancellation_notes)
        else:
            # Set to cancel at end of billing cycle
            sub.auto_renew = False
            sub.end_date = sub.next_billing_date
            sub.churn_reason_id = self.churn_reason_id.id
            sub.cancellation_notes = self.cancellation_notes
            sub.message_post(
                body=_("Cancellation scheduled for end of current cycle (%s). Reason: %s.") % (
                    sub.next_billing_date, self.churn_reason_id.name
                )
            )

        return {'type': 'ir.actions.act_window_close'}
