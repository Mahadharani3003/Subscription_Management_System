# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BrightloopAIAssistant(models.TransientModel):
    _name = 'brightloop.ai.assistant'
    _description = 'Brightloop AI Business Intelligence Assistant'

    query_type = fields.Selection(
        selection=[
            ('mrr_overview', 'What is our current MRR & ARR standing?'),
            ('expiring_soon', 'Which subscriptions are expiring or renewing soon?'),
            ('high_churn_risk', 'Which customers have high churn risk & what are the recommended actions?'),
            ('top_revenue_plans', 'Which subscription plans generate the highest recurring revenue?'),
            ('potential_revenue_loss', 'How much revenue might we lose from cancellations & churn?'),
            ('customer_segments', 'What is our current customer lifecycle & segmentation breakdown?'),
            ('custom_query', 'Ask a Custom Question (Natural Language)...'),
        ],
        string='Business Question',
        default='mrr_overview',
        required=True,
        help="Select a core analytical question or type a custom inquiry."
    )
    custom_prompt = fields.Char(
        string='Custom Question',
        placeholder='e.g., How much revenue is at risk of churning this quarter?',
        help="Type your question. The engine parses key business concepts against live Odoo data."
    )
    response_html = fields.Html(
        string='AI Live Intelligence Briefing',
        readonly=True,
        help="Deterministic, explainable intelligence computed directly from active database records."
    )
    records_analyzed = fields.Integer(
        string='Live Records Analyzed',
        readonly=True
    )
    analysis_timestamp = fields.Datetime(
        string='Analysis Timestamp',
        readonly=True
    )

    def action_ask(self):
        """Process question against live Odoo records and format explainable briefing."""
        self.ensure_one()
        q_type = self.query_type

        # Natural language keyword dispatch if custom query
        if q_type == 'custom_query':
            prompt = (self.custom_prompt or '').lower().strip()
            if not prompt:
                raise UserError(_("Please enter your question in the text box."))
            if any(k in prompt for k in ('mrr', 'arr', 'recurring', 'monthly revenue', 'annual revenue')):
                q_type = 'mrr_overview'
            elif any(k in prompt for k in ('expir', 'renew', 'ending', 'soon', 'upcoming')):
                q_type = 'expiring_soon'
            elif any(k in prompt for k in ('churn', 'risk', 'hazard', 'delinquent', 'danger', 'at risk')):
                q_type = 'high_churn_risk'
            elif any(k in prompt for k in ('plan', 'tier', 'product', 'highest revenue', 'top plan')):
                q_type = 'top_revenue_plans'
            elif any(k in prompt for k in ('loss', 'lose', 'lost', 'cancellation loss', 'leakage')):
                q_type = 'potential_revenue_loss'
            elif any(k in prompt for k in ('segment', 'lifecycle', 'cohort', 'tenure', 'vip', 'starter')):
                q_type = 'customer_segments'
            else:
                return self._render_fallback_response(prompt)

        # Dispatch deterministic query handler
        handlers = {
            'mrr_overview': self._analyze_mrr_overview,
            'expiring_soon': self._analyze_expiring_soon,
            'high_churn_risk': self._analyze_high_churn_risk,
            'top_revenue_plans': self._analyze_top_revenue_plans,
            'potential_revenue_loss': self._analyze_potential_revenue_loss,
            'customer_segments': self._analyze_customer_segments,
        }

        handler = handlers.get(q_type, self._analyze_mrr_overview)
        res_html, count = handler()

        self.write({
            'response_html': res_html,
            'records_analyzed': count,
            'analysis_timestamp': fields.Datetime.now(),
        })

        # Reopen same wizard form with answers populated
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    # --- Analytical Handlers (Zero hallucination, live ORM queries) ---

    def _analyze_mrr_overview(self):
        Sub = self.env['brightloop.subscription']
        active_subs = Sub.search([('state', '=', 'active')])
        paused_subs = Sub.search([('state', '=', 'paused')])
        past_due_subs = Sub.search([('state', '=', 'past_due')])

        total_mrr = sum(active_subs.mapped('mrr'))
        total_arr = sum(active_subs.mapped('arr'))
        paused_mrr = sum(paused_subs.mapped('mrr'))
        past_due_mrr = sum(past_due_subs.mapped('mrr'))

        currency = self.env.company.currency_id.symbol or '$'

        html = f"""
        <div class="brightloop-ai-response p-3" style="font-family: inherit;">
            <div class="d-flex align-items-center mb-3">
                <span class="badge bg-success p-2 me-2" style="font-size: 1rem;"><i class="fa fa-line-chart me-1"></i> Live MRR & ARR Intelligence</span>
                <span class="text-muted small">Validated against {len(active_subs)} active contract(s)</span>
            </div>
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="card bg-light border-0 shadow-sm p-3 text-center">
                        <small class="text-muted fw-bold">ACTIVE MRR</small>
                        <h3 class="text-primary mb-0 mt-1">{currency}{total_mrr:,.2f}</h3>
                        <small class="text-muted">Monthly Recurring</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light border-0 shadow-sm p-3 text-center">
                        <small class="text-muted fw-bold">ANNUAL RUN RATE (ARR)</small>
                        <h3 class="text-success mb-0 mt-1">{currency}{total_arr:,.2f}</h3>
                        <small class="text-muted">12x Normalized Run Rate</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light border-0 shadow-sm p-3 text-center">
                        <small class="text-muted fw-bold">PAST DUE REVENUE</small>
                        <h3 class="text-danger mb-0 mt-1">{currency}{past_due_mrr:,.2f}</h3>
                        <small class="text-danger">{len(past_due_subs)} delinquent contract(s)</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light border-0 shadow-sm p-3 text-center">
                        <small class="text-muted fw-bold">PAUSED REVENUE</small>
                        <h3 class="text-warning mb-0 mt-1">{currency}{paused_mrr:,.2f}</h3>
                        <small class="text-warning">{len(paused_subs)} paused contract(s)</small>
                    </div>
                </div>
            </div>
            <div class="alert alert-info border-0 shadow-sm">
                <strong><i class="fa fa-info-circle me-1"></i> Executive Insight:</strong>
                Your recurring engine commands <strong>{currency}{total_mrr:,.2f}/mo</strong>.
                {"Immediate attention is warranted on " + str(len(past_due_subs)) + " past-due accounts representing " + currency + f"{past_due_mrr:,.2f}/mo in billing friction." if past_due_subs else "All active subscriptions are currently in healthy billing status."}
            </div>
        </div>
        """
        return html, len(active_subs) + len(paused_subs) + len(past_due_subs)

    def _analyze_expiring_soon(self):
        Sub = self.env['brightloop.subscription']
        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=14)

        subs = Sub.search([
            ('state', 'in', ('active', 'past_due')),
            ('next_billing_date', '>=', today),
            ('next_billing_date', '<=', horizon),
        ], order='next_billing_date asc', limit=10)

        currency = self.env.company.currency_id.symbol or '$'
        total_expected = sum(subs.mapped('expected_renewal_revenue'))

        rows = ""
        for s in subs:
            urgency_badge = "bg-danger" if s.days_to_renewal <= 3 else "bg-warning text-dark"
            risk_badge = "bg-success" if s.churn_risk_level == 'low' else ("bg-warning text-dark" if s.churn_risk_level == 'medium' else "bg-danger")
            rows += f"""
            <tr>
                <td><strong>{s.name}</strong></td>
                <td>{s.partner_id.name or 'N/A'}</td>
                <td>{s.plan_id.name or 'N/A'}</td>
                <td>{s.next_billing_date} <span class="badge {urgency_badge} ms-1">{s.days_to_renewal}d</span></td>
                <td><span class="badge {risk_badge}">{s.churn_risk_level.title()}</span></td>
                <td>{currency}{s.recurring_total:,.2f}</td>
                <td class="text-success fw-bold">{currency}{s.expected_renewal_revenue:,.2f}</td>
                <td><small class="text-muted">{s.retention_recommendation or 'Standard renewal'}</small></td>
            </tr>
            """

        if not rows:
            rows = "<tr><td colspan='8' class='text-center text-muted py-3'>No subscriptions are renewing within the next 14 days.</td></tr>"

        html = f"""
        <div class="brightloop-ai-response p-3">
            <div class="d-flex align-items-center mb-3">
                <span class="badge bg-primary p-2 me-2" style="font-size: 1rem;"><i class="fa fa-calendar-check-o me-1"></i> Renewal Timeline (Next 14 Days)</span>
                <span class="text-muted small">Target Window: {today} to {horizon}</span>
            </div>
            <div class="alert alert-secondary border-0 mb-3 d-flex justify-content-between align-items-center">
                <span>Identified <strong>{len(subs)}</strong> subscription(s) renewing soon.</span>
                <span class="fs-6">Expected Weighted Renewal Inflow: <strong class="text-success">{currency}{total_expected:,.2f}</strong></span>
            </div>
            <div class="table-responsive">
                <table class="table table-sm table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Subscription</th>
                            <th>Customer</th>
                            <th>Plan</th>
                            <th>Renewal Date</th>
                            <th>Risk</th>
                            <th>Cycle Total</th>
                            <th>Expected Revenue</th>
                            <th>Recommended Retention Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        """
        return html, len(subs)

    def _analyze_high_churn_risk(self):
        Sub = self.env['brightloop.subscription']
        high_risk_subs = Sub.search([
            ('churn_risk_level', '=', 'high'),
            ('state', 'in', ('active', 'past_due', 'paused'))
        ], order='arr desc', limit=12)

        currency = self.env.company.currency_id.symbol or '$'
        total_arr_loss = sum(high_risk_subs.mapped('predicted_loss_arr'))

        rows = ""
        for s in high_risk_subs:
            state_badge = "bg-danger" if s.state == 'past_due' else "bg-warning text-dark"
            rows += f"""
            <tr>
                <td><strong>{s.name}</strong></td>
                <td>{s.partner_id.name or 'N/A'}</td>
                <td><span class="badge {state_badge}">{s.state.replace('_', ' ').title()}</span></td>
                <td><strong class="text-danger">{s.health_score}/100</strong> ({s.renewal_probability}% Renew Prob)</td>
                <td><small class="text-danger">{s.churn_risk_factors or 'Multiple risk triggers'}</small></td>
                <td class="text-danger fw-bold">{currency}{s.predicted_loss_arr:,.2f}</td>
                <td><span class="badge bg-info text-dark">{s.churn_confidence.title() if s.churn_confidence else 'Standard'}</span></td>
                <td><small class="fw-semibold text-primary">{s.retention_recommendation or 'Proactive customer outreach.'}</small></td>
            </tr>
            """

        if not rows:
            rows = "<tr><td colspan='8' class='text-center text-success py-3'><i class='fa fa-check-circle me-1'></i> Excellent! No active or delinquent subscriptions are currently flagged as High Churn Risk.</td></tr>"

        html = f"""
        <div class="brightloop-ai-response p-3">
            <div class="d-flex align-items-center mb-3">
                <span class="badge bg-danger p-2 me-2" style="font-size: 1rem;"><i class="fa fa-exclamation-triangle me-1"></i> High Churn Hazard Diagnostics & Retention Matrix</span>
                <span class="text-muted small">Total Flagged: {len(high_risk_subs)}</span>
            </div>
            <div class="alert alert-danger border-0 d-flex justify-content-between align-items-center mb-3">
                <span><strong>Priority Action Required:</strong> {len(high_risk_subs)} customer contract(s) exhibit critical churn triggers.</span>
                <span class="fs-6">Total ARR at Risk: <strong>{currency}{total_arr_loss:,.2f}</strong></span>
            </div>
            <div class="table-responsive">
                <table class="table table-sm table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Ref</th>
                            <th>Customer</th>
                            <th>Status</th>
                            <th>Health</th>
                            <th>Identified Churn Triggers</th>
                            <th>ARR at Risk</th>
                            <th>Confidence</th>
                            <th>Actionable Retention Plan</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        """
        return html, len(high_risk_subs)

    def _analyze_top_revenue_plans(self):
        Plan = self.env['brightloop.plan']
        plans = Plan.search([('active', '=', True)])
        currency = self.env.company.currency_id.symbol or '$'

        plan_stats = []
        for p in plans:
            active_subs = p.subscription_ids.filtered(lambda s: s.state == 'active')
            mrr = sum(active_subs.mapped('mrr'))
            arr = sum(active_subs.mapped('arr'))
            plan_stats.append({
                'name': p.name,
                'cadence': dict(p._fields['billing_interval'].selection).get(p.billing_interval, p.billing_interval),
                'price': p.price,
                'count': len(active_subs),
                'mrr': mrr,
                'arr': arr,
            })

        plan_stats.sort(key=lambda x: x['mrr'], reverse=True)
        total_system_mrr = sum(x['mrr'] for x in plan_stats) or 1.0

        rows = ""
        rank = 1
        for ps in plan_stats:
            share = (ps['mrr'] / total_system_mrr) * 100.0
            rows += f"""
            <tr>
                <td class="fw-bold text-center">#{rank}</td>
                <td><strong>{ps['name']}</strong></td>
                <td>{currency}{ps['price']:,.2f} / {ps['cadence']}</td>
                <td class="text-center"><span class="badge bg-secondary">{ps['count']}</span></td>
                <td class="fw-bold text-primary">{currency}{ps['mrr']:,.2f}</td>
                <td class="fw-bold text-success">{currency}{ps['arr']:,.2f}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress flex-grow-1 me-2" style="height: 6px;">
                            <div class="progress-bar bg-primary" style="width: {share:.1f}%;"></div>
                        </div>
                        <small class="text-muted">{share:.1f}%</small>
                    </div>
                </td>
            </tr>
            """
            rank += 1

        html = f"""
        <div class="brightloop-ai-response p-3">
            <div class="d-flex align-items-center mb-3">
                <span class="badge bg-dark p-2 me-2" style="font-size: 1rem;"><i class="fa fa-trophy me-1"></i> Subscription Plan Revenue Hierarchy</span>
                <span class="text-muted small">Live across {len(plans)} active tiers</span>
            </div>
            <div class="table-responsive">
                <table class="table table-sm table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th class="text-center" style="width: 50px;">Rank</th>
                            <th>Plan Tier</th>
                            <th>Unit Pricing</th>
                            <th class="text-center">Active Subs</th>
                            <th>MRR Contribution</th>
                            <th>ARR Run Rate</th>
                            <th>Revenue Share %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        """
        return html, len(plans)

    def _analyze_potential_revenue_loss(self):
        Sub = self.env['brightloop.subscription']
        subs = Sub.search([('state', 'in', ('active', 'past_due', 'paused'))])
        currency = self.env.company.currency_id.symbol or '$'

        total_system_arr = sum(subs.mapped('arr'))
        total_loss_arr = sum(subs.mapped('predicted_loss_arr'))
        overall_loss_pct = (total_loss_arr / total_system_arr * 100.0) if total_system_arr else 0.0

        high_risk_loss = sum(subs.filtered(lambda s: s.churn_risk_level == 'high').mapped('predicted_loss_arr'))
        med_risk_loss = sum(subs.filtered(lambda s: s.churn_risk_level == 'medium').mapped('predicted_loss_arr'))
        low_risk_loss = sum(subs.filtered(lambda s: s.churn_risk_level == 'low').mapped('predicted_loss_arr'))

        html = f"""
        <div class="brightloop-ai-response p-3">
            <div class="d-flex align-items-center mb-3">
                <span class="badge bg-warning text-dark p-2 me-2" style="font-size: 1rem;"><i class="fa fa-shield me-1"></i> Revenue Risk & Churn Loss Forecast</span>
                <span class="text-muted small">Actuarial Loss Model across {len(subs)} contracts</span>
            </div>
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <div class="card bg-light border-0 shadow-sm p-3 text-center">
                        <small class="text-muted fw-bold">TOTAL COMMITTED ARR</small>
                        <h4 class="text-dark mb-0 mt-1">{currency}{total_system_arr:,.2f}</h4>
                        <small class="text-muted">Total annual book of business</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-light border-0 shadow-sm p-3 text-center border-danger">
                        <small class="text-danger fw-bold">PREDICTED ANNUAL LOSS</small>
                        <h4 class="text-danger mb-0 mt-1">{currency}{total_loss_arr:,.2f}</h4>
                        <small class="text-danger fw-semibold">{overall_loss_pct:.1f}% expected annual attrition</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-light border-0 shadow-sm p-3 text-center border-success">
                        <small class="text-success fw-bold">PROTECTED RETAINED ARR</small>
                        <h4 class="text-success mb-0 mt-1">{currency}{(total_system_arr - total_loss_arr):,.2f}</h4>
                        <small class="text-success fw-semibold">{(100.0 - overall_loss_pct):.1f}% expected retention</small>
                    </div>
                </div>
            </div>
            <div class="card border-0 shadow-sm p-3">
                <h6 class="fw-bold mb-3">Attrition Exposure Breakdown by Risk Tier</h6>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span><span class="badge bg-danger me-2">High Risk</span> Immediate Attrition Threat</span>
                        <strong class="text-danger">{currency}{high_risk_loss:,.2f}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span><span class="badge bg-warning text-dark me-2">Medium Risk</span> Moderate Hazard (Proactive Engagement Required)</span>
                        <strong class="text-warning">{currency}{med_risk_loss:,.2f}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span><span class="badge bg-success me-2">Low Risk</span> Residual Statistical Friction</span>
                        <strong class="text-muted">{currency}{low_risk_loss:,.2f}</strong>
                    </li>
                </ul>
            </div>
        </div>
        """
        return html, len(subs)

    def _analyze_customer_segments(self):
        Partner = self.env['res.partner']
        partners = Partner.search([('subscription_count', '>', 0)])
        currency = self.env.company.currency_id.symbol or '$'

        stage_counts = {'new': 0, 'regular': 0, 'long_term': 0, 'at_risk': 0, 'churned': 0, 'none': 0}
        tier_counts = {'vip': 0, 'growth': 0, 'starter': 0, 'at_risk': 0, 'churned': 0, 'none': 0}
        total_risk = sum(partners.mapped('total_arr_at_risk'))

        for p in partners:
            s = p.customer_lifecycle_stage or 'none'
            t = p.subscription_segment or 'none'
            stage_counts[s] = stage_counts.get(s, 0) + 1
            tier_counts[t] = tier_counts.get(t, 0) + 1

        total = len(partners) or 1

        html = f"""
        <div class="brightloop-ai-response p-3">
            <div class="d-flex align-items-center mb-3">
                <span class="badge bg-info text-dark p-2 me-2" style="font-size: 1rem;"><i class="fa fa-users me-1"></i> Customer Cohort & Lifecycle Intelligence</span>
                <span class="text-muted small">Analyzed {total} subscribing account(s)</span>
            </div>
            <div class="row g-3 mb-3">
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm p-3 h-100">
                        <h6 class="fw-bold mb-3 text-primary"><i class="fa fa-clock-o me-1"></i> Lifecycle Tenure Stages</h6>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between">
                                <span><i class="fa fa-star text-success me-1"></i> Long-term Champions (>365d)</span>
                                <strong>{stage_counts['long_term']} ({stage_counts['long_term']/total*100:.1f}%)</strong>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span><i class="fa fa-check text-primary me-1"></i> Steady Established (90d-365d)</span>
                                <strong>{stage_counts['regular']} ({stage_counts['regular']/total*100:.1f}%)</strong>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span><i class="fa fa-leaf text-info me-1"></i> New Onboarding (&lt;90d)</span>
                                <strong>{stage_counts['new']} ({stage_counts['new']/total*100:.1f}%)</strong>
                            </li>
                            <li class="list-group-item d-flex justify-content-between text-danger">
                                <span><i class="fa fa-warning me-1"></i> At-Risk Delinquent</span>
                                <strong>{stage_counts['at_risk']} ({stage_counts['at_risk']/total*100:.1f}%)</strong>
                            </li>
                            <li class="list-group-item d-flex justify-content-between text-muted">
                                <span><i class="fa fa-times-circle me-1"></i> Former Churned</span>
                                <strong>{stage_counts['churned']} ({stage_counts['churned']/total*100:.1f}%)</strong>
                            </li>
                        </ul>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm p-3 h-100">
                        <h6 class="fw-bold mb-3 text-success"><i class="fa fa-diamond me-1"></i> Value Segment Tiering</h6>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item d-flex justify-content-between">
                                <span><span class="badge bg-warning text-dark me-2">VIP</span> VIP Enterprise (MRR &ge; $500)</span>
                                <strong>{tier_counts['vip']}</strong>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span><span class="badge bg-primary me-2">Growth</span> Scale & Growth (MRR &ge; $90)</span>
                                <strong>{tier_counts['growth']}</strong>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span><span class="badge bg-secondary me-2">Starter</span> Standard Starter</span>
                                <strong>{tier_counts['starter']}</strong>
                            </li>
                            <li class="list-group-item d-flex justify-content-between">
                                <span class="text-danger fw-semibold"><i class="fa fa-exclamation me-1"></i> Aggregate ARR at Risk</span>
                                <strong class="text-danger">{currency}{total_risk:,.2f}</strong>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """
        return html, total

    def _render_fallback_response(self, prompt):
        html = f"""
        <div class="brightloop-ai-response p-3">
            <div class="alert alert-warning border-0 shadow-sm">
                <h5><i class="fa fa-question-circle me-1"></i> Natural Language Interpretation</h5>
                <p>We received your inquiry: <em>"{prompt}"</em></p>
                <p class="mb-0">To ensure 100% data fidelity without generative fabrication, Brightloop maps queries directly to live ERP records. Please try asking about:</p>
                <ul class="mt-2 mb-0">
                    <li><strong>MRR or ARR</strong>: "What is our current monthly recurring revenue?"</li>
                    <li><strong>Renewals</strong>: "Which contracts are expiring in the next 14 days?"</li>
                    <li><strong>Churn</strong>: "Show me high churn risk accounts and retention recommendations."</li>
                    <li><strong>Plans</strong>: "Which plans generate the highest revenue?"</li>
                    <li><strong>Revenue Loss</strong>: "How much ARR could be lost to churn?"</li>
                    <li><strong>Segmentation</strong>: "Show customer lifecycle stages and VIP tiers."</li>
                </ul>
            </div>
        </div>
        """
        self.write({
            'response_html': html,
            'records_analyzed': 0,
            'analysis_timestamp': fields.Datetime.now(),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
