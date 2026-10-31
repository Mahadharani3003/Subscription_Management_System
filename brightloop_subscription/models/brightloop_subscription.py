# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

import logging
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BrightloopSubscription(models.Model):
    _name = 'brightloop.subscription'
    _description = 'Brightloop Subscription Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Subscription Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
        index=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Subscriber / Customer',
        required=True,
        tracking=True,
        index=True,
        help="Customer or organization subscribed to this service."
    )
    plan_id = fields.Many2one(
        comodel_name='brightloop.plan',
        string='Subscription Plan',
        required=True,
        tracking=True,
        index=True,
        help="Selected subscription tier defining cadence and base pricing."
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help="Company operating this subscription."
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='plan_id.currency_id',
        store=True,
        readonly=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Account Manager',
        default=lambda self: self.env.user,
        tracking=True,
        help="Internal manager handling this account."
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('trial', 'Free Trial'),
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('past_due', 'Past Due'),
            ('cancelled', 'Cancelled'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        index=True,
        copy=False,
        help="Operational lifecycle stage of the subscription contract."
    )
    start_date = fields.Date(
        string='Start Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
        help="Date when the subscription officially commences."
    )
    trial_end_date = fields.Date(
        string='Trial Expiration Date',
        tracking=True,
        help="End date of the complimentary trial period."
    )
    next_billing_date = fields.Date(
        string='Next Billing Date',
        tracking=True,
        index=True,
        help="Next scheduled date for automated recurring invoice generation."
    )
    end_date = fields.Date(
        string='End / Termination Date',
        tracking=True,
        help="Final date of service contract if fixed-term or cancelled."
    )
    paused_date = fields.Date(
        string='Paused On',
        readonly=True,
        copy=False,
        help="Date when active subscription was suspended."
    )
    auto_renew = fields.Boolean(
        string='Auto Renew',
        default=True,
        tracking=True,
        help="Flag indicating whether contract automatically recurs at cycle end."
    )
    line_ids = fields.One2many(
        comodel_name='brightloop.subscription.line',
        inverse_name='subscription_id',
        string='Add-on Lines & Seats',
        copy=True
    )
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        relation='brightloop_subscription_invoice_rel',
        column1='subscription_id',
        column2='invoice_id',
        string='Invoices',
        readonly=True,
        copy=False,
        help="All billing invoices generated for this subscription."
    )
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_count',
        help="Total number of invoices generated."
    )
    recurring_total = fields.Monetary(
        string='Recurring Total',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
        tracking=True,
        help="Total billing amount due on each recurring cycle."
    )
    mrr = fields.Monetary(
        string='Monthly Recurring Revenue (MRR)',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
        tracking=True,
        help="Normalized revenue earned on a 30-day monthly cadence."
    )
    arr = fields.Monetary(
        string='Annual Recurring Revenue (ARR)',
        currency_field='currency_id',
        compute='_compute_financials',
        store=True,
        help="Normalized annual recurring value (MRR * 12)."
    )
    churn_reason_id = fields.Many2one(
        comodel_name='brightloop.churn.reason',
        string='Churn Reason',
        tracking=True,
        help="Primary reason for cancellation or non-renewal."
    )
    cancellation_notes = fields.Text(
        string='Cancellation / Offboarding Notes',
        tracking=True,
        help="Internal notes or customer feedback collected during offboarding."
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'The Subscription reference must be unique per company!')
    ]

    # --- Computations & Constraints ---

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for sub in self:
            sub.invoice_count = len(sub.invoice_ids)

    @api.depends('plan_id', 'plan_id.price', 'plan_id.billing_interval', 'plan_id.billing_interval_count', 'line_ids.subtotal')
    def _compute_financials(self):
        for sub in self:
            plan = sub.plan_id
            base_price = plan.price if plan else 0.0
            addons_sum = sum(sub.line_ids.mapped('subtotal'))
            cycle_total = base_price + addons_sum
            sub.recurring_total = cycle_total

            # MRR normalization
            if not plan or not plan.billing_interval_count or plan.billing_interval_count <= 0:
                sub.mrr = cycle_total
            else:
                interval = plan.billing_interval
                count = float(plan.billing_interval_count)
                if interval == 'month':
                    sub.mrr = cycle_total / count
                elif interval == 'year':
                    sub.mrr = cycle_total / (12.0 * count)
                elif interval == 'day':
                    sub.mrr = (cycle_total / count) * 30.0
                else:
                    sub.mrr = cycle_total

            sub.arr = sub.mrr * 12.0

    @api.constrains('start_date', 'end_date', 'next_billing_date')
    def _check_dates_consistency(self):
        for sub in self:
            if sub.end_date and sub.start_date and sub.end_date < sub.start_date:
                raise ValidationError(_("End Date (%s) cannot precede Start Date (%s).", sub.end_date, sub.start_date))

    # --- Onchange Handlers ---

    @api.onchange('plan_id')
    def _onchange_plan_id(self):
        if self.plan_id:
            today = self.start_date or fields.Date.context_today(self)
            if self.plan_id.trial_period_days > 0:
                self.trial_end_date = today + relativedelta(days=self.plan_id.trial_period_days)
                self.next_billing_date = self.trial_end_date
            else:
                self.trial_end_date = False
                self.next_billing_date = today

    # --- CRUD Overrides ---

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                seq_code = 'brightloop.subscription'
                vals['name'] = self.env['ir.sequence'].next_by_code(seq_code) or _('New')
        return super().create(vals_list)

    def write(self, vals):
        # Automatically update next billing date if plan changes on draft
        res = super().write(vals)
        return res

    def unlink(self):
        for sub in self:
            if sub.state not in ('draft', 'cancelled'):
                raise UserError(_("You cannot delete a subscription that is %s. Please cancel it first.", sub.state))
        return super().unlink()

    # --- Business Logic & State Transitions ---

    def _get_cadence_delta(self):
        """Helper to return dateutil relativedelta for current plan cadence."""
        self.ensure_one()
        plan = self.plan_id
        if not plan:
            return relativedelta(months=1)
        count = plan.billing_interval_count or 1
        interval = plan.billing_interval
        if interval == 'day':
            return relativedelta(days=count)
        elif interval == 'year':
            return relativedelta(years=count)
        return relativedelta(months=count)

    def action_start_trial(self):
        """Transition from Draft to Free Trial."""
        for sub in self:
            if sub.state != 'draft':
                raise UserError(_("Trial can only be initiated from Draft status."))
            trial_days = sub.plan_id.trial_period_days if sub.plan_id else 0
            if trial_days <= 0:
                raise UserError(_("The selected plan '%s' does not provide a trial period.", sub.plan_id.name))
            start = sub.start_date or fields.Date.context_today(sub)
            sub.trial_end_date = start + relativedelta(days=trial_days)
            sub.next_billing_date = sub.trial_end_date
            sub.state = 'trial'
            sub.message_post(body=_("Subscription moved to <b>Free Trial</b> until %s.", sub.trial_end_date))

    def action_activate(self):
        """Confirm and activate the subscription contract."""
        for sub in self:
            if sub.state not in ('draft', 'trial'):
                raise UserError(_("Only Draft or Trial subscriptions can be activated."))
            if not sub.next_billing_date:
                sub.next_billing_date = fields.Date.context_today(sub)
            sub.state = 'active'
            sub.message_post(body=_("Subscription confirmed and <b>Activated</b>. Next billing scheduled for %s.", sub.next_billing_date))

    def action_pause(self):
        """Pause recurring services and billing."""
        for sub in self:
            if sub.state != 'active':
                raise UserError(_("Only Active subscriptions can be paused."))
            sub.state = 'paused'
            sub.paused_date = fields.Date.context_today(sub)
            sub.message_post(body=_("Subscription has been <b>Paused</b> on %s.", sub.paused_date))

    def action_resume(self):
        """Resume paused subscription and adjust billing schedule accordingly."""
        for sub in self:
            if sub.state != 'paused':
                raise UserError(_("Only Paused subscriptions can be resumed."))
            today = fields.Date.context_today(sub)
            # Adjust next billing date forward by days paused
            if sub.paused_date and sub.next_billing_date:
                paused_duration = (today - sub.paused_date).days
                if paused_duration > 0:
                    sub.next_billing_date = sub.next_billing_date + relativedelta(days=paused_duration)
            sub.state = 'active'
            sub.paused_date = False
            sub.message_post(body=_("Subscription <b>Resumed</b>. Next billing shifted to %s.", sub.next_billing_date))

    def action_cancel(self, churn_reason_id=None, notes=None):
        """Terminate the subscription with optional churn feedback."""
        for sub in self:
            if sub.state in ('cancelled', 'closed'):
                continue
            vals = {
                'state': 'cancelled',
                'end_date': fields.Date.context_today(sub),
            }
            if churn_reason_id:
                vals['churn_reason_id'] = churn_reason_id
            if notes:
                vals['cancellation_notes'] = notes
            sub.write(vals)
            reason_str = sub.churn_reason_id.name if sub.churn_reason_id else _('Unspecified')
            sub.message_post(body=_("Subscription <b>Cancelled</b>. Reason: %s.", reason_str))

    def action_close(self):
        """Close/Expire subscription upon term conclusion or non-payment."""
        for sub in self:
            sub.state = 'closed'
            sub.end_date = fields.Date.context_today(sub)
            sub.message_post(body=_("Subscription contract marked as <b>Closed / Expired</b>."))

    def action_renew(self):
        """Manually trigger immediate recurring invoice generation."""
        self.ensure_one()
        return self.action_generate_invoice()

    def action_generate_invoice(self):
        """
        Generate customer invoice (account.move) for the current billing cycle,
        advance next_billing_date, and record the invoice link.
        """
        Invoice = self.env['account.move']
        created_invoices = self.env['account.move']

        for sub in self:
            if sub.state not in ('active', 'past_due'):
                raise UserError(_("Invoices can only be generated for Active or Past Due subscriptions."))

            # 1. Prepare invoice lines
            invoice_lines = []
            # Plan base service item
            plan_product = sub.plan_id.product_id
            invoice_lines.append((0, 0, {
                'product_id': plan_product.id,
                'name': f"{sub.plan_id.name} - {sub.name}",
                'quantity': 1.0,
                'price_unit': sub.plan_id.price,
                'tax_ids': [(6, 0, plan_product.taxes_id.filtered(lambda t: t.company_id == sub.company_id).ids)],
            }))

            # Add-on seat items
            for line in sub.line_ids:
                invoice_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name or line.product_id.name,
                    'quantity': line.quantity,
                    'price_unit': line.unit_price,
                    'tax_ids': [(6, 0, line.product_id.taxes_id.filtered(lambda t: t.company_id == sub.company_id).ids)],
                }))

            # 2. Prepare invoice values
            inv_vals = {
                'move_type': 'out_invoice',
                'partner_id': sub.partner_id.id,
                'currency_id': sub.currency_id.id,
                'company_id': sub.company_id.id,
                'invoice_date': fields.Date.context_today(sub),
                'invoice_origin': sub.name,
                'invoice_line_ids': invoice_lines,
            }

            # 3. Create invoice
            new_inv = Invoice.sudo().create(inv_vals)
            sub.invoice_ids = [(4, new_inv.id)]
            created_invoices |= new_inv

            # 4. Advance next_billing_date
            current_next = sub.next_billing_date or fields.Date.context_today(sub)
            delta = sub._get_cadence_delta()
            sub.next_billing_date = current_next + delta

            # 5. Post notification
            sub.message_post(
                body=_("Generated recurring billing invoice <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a> for amount %s %s. Next billing date: %s.") % (
                    new_inv.id, new_inv.name or _('Draft Invoice'), new_inv.amount_total, sub.currency_id.symbol, sub.next_billing_date
                )
            )

        if len(created_invoices) == 1:
            return {
                'name': _('Customer Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': created_invoices.id,
                'view_mode': 'form',
            }
        return created_invoices

    def action_view_invoices(self):
        """Smart button action to drill down into generated invoices."""
        self.ensure_one()
        action = {
            'name': _('Invoices - %s', self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'default_move_type': 'out_invoice', 'default_partner_id': self.partner_id.id},
        }
        if len(self.invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.invoice_ids.ids)],
            })
        return action

    # --- Automated Cron Schedulers ---

    @api.model
    def _cron_recurring_billing(self):
        """
        Daily scheduler: Query active subscriptions due for billing and generate invoices.
        """
        today = fields.Date.context_today(self)
        _logger.info("Executing Brightloop recurring billing cron for date: %s", today)
        due_subscriptions = self.search([
            ('state', '=', 'active'),
            ('next_billing_date', '<=', today),
        ])
        _logger.info("Found %d subscription(s) due for recurring billing.", len(due_subscriptions))

        success_count = 0
        for sub in due_subscriptions:
            try:
                sub.action_generate_invoice()
                success_count += 1
            except Exception as e:
                _logger.error("Failed to generate recurring invoice for subscription %s: %s", sub.name, str(e))

        _logger.info("Completed Brightloop billing cron. Successfully billed %d subscriptions.", success_count)

    @api.model
    def _cron_check_grace_periods(self):
        """
        Daily scheduler: Identify subscriptions with overdue unpaid invoices.
        Transitions state to 'past_due' or auto-cancels if grace threshold is exceeded.
        """
        today = fields.Date.context_today(self)
        active_or_due = self.search([('state', 'in', ('active', 'past_due'))])

        for sub in active_or_due:
            unpaid_invoices = sub.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.payment_state in ('not_paid', 'partial'))
            if not unpaid_invoices:
                # If was past_due and all invoices are settled, return to active
                if sub.state == 'past_due':
                    sub.state = 'active'
                    sub.message_post(body=_("All outstanding invoices settled. Subscription restored to <b>Active</b>."))
                continue

            # Check oldest overdue invoice
            grace_days = sub.plan_id.grace_period_days or 7
            overdue_candidates = unpaid_invoices.filtered(lambda inv: inv.invoice_date_due and inv.invoice_date_due < today)
            if overdue_candidates:
                oldest_due = min(overdue_candidates.mapped('invoice_date_due'))
                days_overdue = (today - oldest_due).days

                if days_overdue >= grace_days:
                    if sub.state == 'active':
                        sub.state = 'past_due'
                        sub.message_post(
                            body=_("Subscription marked as <b>Past Due</b>. Outstanding invoice overdue by %d days (Grace period: %d days).") % (days_overdue, grace_days)
                        )
                        # Schedule activity for account manager
                        sub.activity_schedule(
                            'mail.mail_activity_data_todo',
                            summary=_("Follow up on Overdue Subscription Payment"),
                            note=_("Customer has unpaid invoices overdue by %d days.") % days_overdue,
                            user_id=sub.user_id.id or self.env.uid
                        )

                    # Auto-close check
                    if sub.plan_id.auto_close_unpaid and days_overdue >= (grace_days * 2):
                        sub.action_close()
                        sub.message_post(body=_("Subscription auto-closed due to prolonged non-payment past final threshold."))
