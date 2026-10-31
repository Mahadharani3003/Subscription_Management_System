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
        index=True,
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
        index=True,
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
        index=True,
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
    last_invoiced_date = fields.Date(
        string='Last Invoiced Date',
        readonly=True,
        copy=False,
        index=True,
        help="Prevents duplicate invoice generation for the same billing window."
    )
    last_renewal_reminder_date = fields.Date(
        string='Last Reminder Date',
        readonly=True,
        copy=False,
        help="Date when upcoming renewal reminder notification was last dispatched."
    )
    end_date = fields.Date(
        string='End / Termination Date',
        tracking=True,
        index=True,
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
        index=True,
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
        index=True,
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

    def unlink(self):
        for sub in self:
            if sub.state not in ('draft', 'cancelled'):
                raise UserError(_("You cannot delete a subscription that is %s. Please cancel it first.", sub.state))
        return super().unlink()

    # --- Helpers ---

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

    # --- Lifecycle State Machine Actions ---

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
        """Confirm and activate the subscription contract, sending automated welcome email."""
        template = self.env.ref('brightloop_subscription.mail_template_subscription_activated', raise_if_not_found=False)

        for sub in self:
            if sub.state not in ('draft', 'trial'):
                raise UserError(_("Only Draft or Trial subscriptions can be activated."))
            if not sub.next_billing_date:
                sub.next_billing_date = fields.Date.context_today(sub)
            sub.state = 'active'
            sub.message_post(body=_("Subscription confirmed and <b>Activated</b>. Next billing scheduled for %s.", sub.next_billing_date))

            # Dispatch welcome notification
            if template:
                try:
                    template.send_mail(sub.id, force_send=True)
                except Exception as e:
                    _logger.warning("Could not send activation mail for sub %s: %s", sub.name, str(e))

    def action_pause(self):
        """Pause recurring services and billing."""
        for sub in self:
            if sub.state != 'active':
                raise UserError(_("Only Active subscriptions can be paused."))
            sub.state = 'paused'
            sub.paused_date = fields.Date.context_today(sub)
            sub.message_post(body=_("Subscription has been <b>Paused</b> on %s. Automated billing suspended.", sub.paused_date))

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
            sub.message_post(body=_("Subscription <b>Resumed</b>. Next billing shifted forward to %s.", sub.next_billing_date))

    def action_cancel(self, churn_reason_id=None, notes=None):
        """Terminate the subscription with churn feedback and send cancellation confirmation."""
        template = self.env.ref('brightloop_subscription.mail_template_subscription_cancelled', raise_if_not_found=False)

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

            if template:
                try:
                    template.send_mail(sub.id, force_send=True)
                except Exception as e:
                    _logger.warning("Could not send cancellation mail for sub %s: %s", sub.name, str(e))

    def action_close(self):
        """Close/Expire subscription upon term conclusion or non-payment."""
        template = self.env.ref('brightloop_subscription.mail_template_subscription_expired', raise_if_not_found=False)

        for sub in self:
            sub.state = 'closed'
            sub.end_date = fields.Date.context_today(sub)
            sub.message_post(body=_("Subscription contract marked as <b>Closed / Expired</b>."))

            if template:
                try:
                    template.send_mail(sub.id, force_send=True)
                except Exception as e:
                    _logger.warning("Could not send expiration mail for sub %s: %s", sub.name, str(e))

    def action_renew(self):
        """Manually trigger immediate recurring invoice generation."""
        self.ensure_one()
        return self.action_generate_invoice()

    # --- Upgrade / Downgrade Business Logic & Proration ---

    def action_change_plan(self, new_plan, apply_now=True):
        """
        Execute subscription plan change (Upgrade / Downgrade).
        Calculates proration if immediate, updates plan, and logs audit trail.
        """
        self.ensure_one()
        if not new_plan or new_plan.id == self.plan_id.id:
            raise UserError(_("Please choose a different plan to upgrade or downgrade."))

        old_plan = self.plan_id
        is_upgrade = new_plan.price > old_plan.price
        change_type = _("Upgrade") if is_upgrade else _("Downgrade")

        if apply_now and self.state == 'active' and self.next_billing_date:
            today = fields.Date.context_today(self)
            # Calculate remaining days in cycle
            cycle_delta = self._get_cadence_delta()
            cycle_start = self.next_billing_date - cycle_delta
            total_cycle_days = max(1, (self.next_billing_date - cycle_start).days)
            remaining_days = max(0, (self.next_billing_date - today).days)

            # Proration factor
            proration_ratio = float(remaining_days) / float(total_cycle_days)
            unused_old_credit = round(old_plan.price * proration_ratio, 2)
            prorated_new_charge = round(new_plan.price * proration_ratio, 2)
            net_adjustment = round(prorated_new_charge - unused_old_credit, 2)

            # Update plan
            self.plan_id = new_plan.id

            # Create proration invoice if positive adjustment
            if net_adjustment > 0:
                inv_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': self.partner_id.id,
                    'currency_id': self.currency_id.id,
                    'company_id': self.company_id.id,
                    'invoice_date': today,
                    'invoice_origin': f"{self.name} ({change_type} Proration)",
                    'invoice_line_ids': [(0, 0, {
                        'product_id': new_plan.product_id.id,
                        'name': f"Prorated {change_type} Adjustment: {old_plan.name} -> {new_plan.name} ({remaining_days}/{total_cycle_days} days)",
                        'quantity': 1.0,
                        'price_unit': net_adjustment,
                    })],
                }
                proration_inv = self.env['account.move'].sudo().create(inv_vals)
                self.invoice_ids = [(4, proration_inv.id)]

            self.message_post(
                body=_("Plan <b>%s</b> executed: <b>%s</b> &rarr; <b>%s</b>. Net proration adjustment: %s %s (%d days remaining in cycle).") % (
                    change_type, old_plan.name, new_plan.name, net_adjustment, self.currency_id.symbol, remaining_days
                )
            )
        else:
            # Change at next cycle
            self.plan_id = new_plan.id
            self.message_post(
                body=_("Plan changed to <b>%s</b>. New pricing takes effect on next billing date (%s).") % (
                    new_plan.name, self.next_billing_date
                )
            )

        # Dispatch notification
        template = self.env.ref('brightloop_subscription.mail_template_subscription_plan_changed', raise_if_not_found=False)
        if template:
            try:
                template.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.warning("Could not send plan change mail for sub %s: %s", self.name, str(e))

    # --- Automated Billing Engine & Idempotency ---

    def action_generate_invoice(self):
        """
        Generate customer invoice (account.move) for the current billing cycle.
        Includes strict idempotency to prevent duplicate invoices for the same cycle.
        """
        Invoice = self.env['account.move']
        created_invoices = self.env['account.move']
        template = self.env.ref('brightloop_subscription.mail_template_subscription_invoiced', raise_if_not_found=False)

        for sub in self:
            if sub.state not in ('active', 'past_due'):
                raise UserError(_("Invoices can only be generated for Active or Past Due subscriptions."))

            today = fields.Date.context_today(sub)

            # --- IDEMPOTENCY GUARD: Check for existing unbilled/open invoice today ---
            existing_open = sub.invoice_ids.filtered(
                lambda inv: inv.invoice_date == today and inv.state in ('draft', 'posted')
            )
            if existing_open:
                _logger.info("Invoice already exists today for subscription %s: %s. Skipping duplicate generation.", sub.name, existing_open[0].name)
                created_invoices |= existing_open[0]
                continue

            # 1. Prepare invoice lines
            invoice_lines = []
            plan_product = sub.plan_id.product_id
            invoice_lines.append((0, 0, {
                'product_id': plan_product.id,
                'name': f"{sub.plan_id.name} - {sub.name}",
                'quantity': 1.0,
                'price_unit': sub.plan_id.price,
                'tax_ids': [(6, 0, plan_product.taxes_id.filtered(lambda t: t.company_id == sub.company_id).ids)],
            }))

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
                'invoice_date': today,
                'invoice_origin': sub.name,
                'invoice_line_ids': invoice_lines,
            }

            # 3. Create invoice with savepoint protection
            with self.env.cr.savepoint():
                new_inv = Invoice.sudo().create(inv_vals)
                sub.invoice_ids = [(4, new_inv.id)]
                sub.last_invoiced_date = today
                created_invoices |= new_inv

                # 4. Advance next_billing_date
                current_next = sub.next_billing_date or today
                delta = sub._get_cadence_delta()
                sub.next_billing_date = current_next + delta

            # 5. Post notification & send email
            sub.message_post(
                body=_("Generated recurring billing invoice <a href='#' data-oe-model='account.move' data-oe-id='%s'>%s</a> for %s %s. Next billing date: %s.") % (
                    new_inv.id, new_inv.name or _('Draft Invoice'), new_inv.amount_total, sub.currency_id.symbol, sub.next_billing_date
                )
            )

            if template:
                try:
                    template.send_mail(sub.id, force_send=True)
                except Exception as e:
                    _logger.warning("Could not send invoice notification mail for sub %s: %s", sub.name, str(e))

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

    # --- Automated Scheduled Actions (Cron Jobs) ---

    @api.model
    def _cron_recurring_billing(self):
        """Daily scheduler: Detect active subscriptions due for billing and generate invoices."""
        today = fields.Date.context_today(self)
        _logger.info("Brightloop Cron: Executing recurring billing check for date %s", today)
        due_subscriptions = self.search([
            ('state', '=', 'active'),
            ('next_billing_date', '<=', today),
        ])
        _logger.info("Found %d subscription(s) due for billing.", len(due_subscriptions))

        success_count = 0
        for sub in due_subscriptions:
            try:
                sub.action_generate_invoice()
                success_count += 1
            except Exception as e:
                _logger.error("Failed recurring invoice generation for sub %s: %s", sub.name, str(e))

        _logger.info("Brightloop Cron: Completed recurring billing. Successfully processed %d contracts.", success_count)

    @api.model
    def _cron_renewal_reminders(self):
        """
        Daily scheduler: Send upcoming renewal reminder notifications 3 days in advance.
        Guards against duplicate notifications in the same cycle.
        """
        today = fields.Date.context_today(self)
        reminder_target_date = today + relativedelta(days=3)
        _logger.info("Brightloop Cron: Checking upcoming renewal reminders due on %s", reminder_target_date)

        upcoming_subs = self.search([
            ('state', '=', 'active'),
            ('auto_renew', '=', True),
            ('next_billing_date', '=', reminder_target_date),
            '|', ('last_renewal_reminder_date', '=', False),
                 ('last_renewal_reminder_date', '<', today - relativedelta(days=15))
        ])

        template = self.env.ref('brightloop_subscription.mail_template_subscription_renewal_reminder', raise_if_not_found=False)

        for sub in upcoming_subs:
            sub.last_renewal_reminder_date = today
            sub.message_post(body=_("Automated renewal reminder dispatched for upcoming billing on %s.") % sub.next_billing_date)
            if template:
                try:
                    template.send_mail(sub.id, force_send=True)
                except Exception as e:
                    _logger.warning("Could not send renewal reminder for sub %s: %s", sub.name, str(e))

    @api.model
    def _cron_check_grace_periods(self):
        """
        Daily scheduler: Identify subscriptions with overdue unpaid invoices using optimized SQL joins.
        Transitions state to 'past_due' and auto-cancels upon final threshold breach.
        """
        today = fields.Date.context_today(self)
        # Optimized query: only fetch subscriptions that actually have posted unpaid invoices
        active_or_due = self.search([
            ('state', 'in', ('active', 'past_due')),
            ('invoice_ids.state', '=', 'posted'),
            ('invoice_ids.payment_state', 'in', ('not_paid', 'partial')),
        ])

        for sub in active_or_due:
            unpaid_invoices = sub.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.payment_state in ('not_paid', 'partial'))
            if not unpaid_invoices:
                if sub.state == 'past_due':
                    sub.state = 'active'
                    sub.message_post(body=_("All outstanding invoices settled. Subscription restored to <b>Active</b>."))
                continue

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

    @api.model
    def _cron_check_expirations(self):
        """Daily scheduler: Transition expired fixed-term subscriptions to Closed using indexed end_date."""
        today = fields.Date.context_today(self)
        expired_subs = self.search([
            ('state', 'in', ('active', 'past_due', 'paused')),
            ('end_date', '!=', False),
            ('end_date', '<=', today),
        ])

        for sub in expired_subs:
            sub.action_close()
            sub.message_post(body=_("Subscription term reached end date (%s). Contract automatically expired.") % sub.end_date)
