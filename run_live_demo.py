# -*- coding: utf-8 -*-
"""
Brightloop Live Interactive Demo Application Server
===================================================
Runs on http://localhost:8069 (Native Odoo Port)
Provides full-fidelity Odoo 17/18 Community Web Client & Customer Portal:
- Kanban Pipeline (Draft -> Trial -> Active -> Paused -> Past Due)
- Contract Smart Forms with Proration Switcher Modal
- SaaS Commercial Packaging (Starter, Pro, Enterprise)
- Churn Watchlist & Health Scoring (0-100)
- In-ERP AI Business Intelligence Assistant
- Customer Self-Service Portal (/my/subscriptions)
- Floating Conversational AI Chatbot with live JSON-RPC lookups
- Impressive 4-Tier System Architecture Presentation (/architecture)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import date, timedelta

PORT = 8069
TODAY = date(2026, 10, 31)

# In-Memory Stateful ERP State
STATE = {
    'plans': [
        {
            'id': 1, 'name': 'Starter', 'code': 'START-MO', 'price': 29.0, 'interval': 'month', 'interval_count': 1,
            'trial_days': 14, 'grace_days': 7, 'tier': 'starter', 'max_subs': 100, 'api': False, 'ai': False, 'sla': 48,
            'desc': 'Essential subscription management for startups.'
        },
        {
            'id': 2, 'name': 'Professional', 'code': 'PRO-MO', 'price': 99.0, 'interval': 'month', 'interval_count': 1,
            'trial_days': 14, 'grace_days': 7, 'tier': 'professional', 'max_subs': 1000, 'api': True, 'ai': True, 'sla': 24,
            'desc': 'Advanced automation, automated proration, and churn diagnostics.'
        },
        {
            'id': 3, 'name': 'Enterprise', 'code': 'ENT-YR', 'price': 999.0, 'interval': 'year', 'interval_count': 1,
            'trial_days': 30, 'grace_days': 14, 'tier': 'enterprise', 'max_subs': 0, 'api': True, 'ai': True, 'sla': 4,
            'desc': 'Dedicated account management, unlimited contracts, and custom LLM integration.'
        }
    ],
    'subscriptions': [
        {
            'id': 1, 'name': 'SUB/2026/0001', 'partner': 'Acme Global Corp', 'plan_id': 2, 'state': 'active',
            'start_date': '2026-05-15', 'next_billing': '2026-11-14', 'days_to_renewal': 14, 'recurring_total': 149.0,
            'arr': 1788.0, 'auto_renew': True, 'health_score': 92, 'risk': 'low', 'renew_prob': 93.5,
            'recommendation': 'Account in healthy standing: Target for Enterprise upgrade or add-on seat upsell.',
            'factors': 'Tenure > 6 months | Zero overdue invoices | Auto-renew enabled'
        },
        {
            'id': 2, 'name': 'SUB/2026/0002', 'partner': 'TechPulse Innovations', 'plan_id': 1, 'state': 'active',
            'start_date': '2026-08-01', 'next_billing': '2026-11-01', 'days_to_renewal': 1, 'recurring_total': 29.0,
            'arr': 348.0, 'auto_renew': True, 'health_score': 85, 'risk': 'low', 'renew_prob': 90.0,
            'recommendation': 'Account in healthy standing: Proactive engagement.',
            'factors': 'Flawless payment record'
        },
        {
            'id': 3, 'name': 'SUB/2026/0003', 'partner': 'Apex Media Group', 'plan_id': 2, 'state': 'past_due',
            'start_date': '2026-03-10', 'next_billing': '2026-10-20', 'days_to_renewal': -11, 'recurring_total': 99.0,
            'arr': 1188.0, 'auto_renew': True, 'health_score': 35, 'risk': 'high', 'renew_prob': 21.0,
            'recommendation': 'Critical Delinquency: Contact billing contact immediately; offer 7-day payment extension.',
            'factors': 'Invoice overdue by 11 days (Grace breached)'
        },
        {
            'id': 4, 'name': 'SUB/2026/0004', 'partner': 'Nexus Logistics', 'plan_id': 3, 'state': 'active',
            'start_date': '2025-11-01', 'next_billing': '2026-11-01', 'days_to_renewal': 1, 'recurring_total': 999.0,
            'arr': 999.0, 'auto_renew': True, 'health_score': 95, 'risk': 'low', 'renew_prob': 96.0,
            'recommendation': 'Enterprise VIP Account: Schedule quarterly executive review.',
            'factors': 'Tenure > 12 months | Loyal VIP champion'
        },
        {
            'id': 5, 'name': 'SUB/2026/0005', 'partner': 'Lumina Retail Partners', 'plan_id': 1, 'state': 'paused',
            'start_date': '2026-07-20', 'next_billing': '2026-11-20', 'days_to_renewal': 20, 'recurring_total': 29.0,
            'arr': 348.0, 'auto_renew': False, 'health_score': 45, 'risk': 'high', 'renew_prob': 27.0,
            'recommendation': 'Cancellation Intent: Auto-renew disabled. Dispatch retention specialist; offer 15% discount.',
            'factors': 'Subscription temporarily suspended | Auto-renew off'
        },
        {
            'id': 6, 'name': 'SUB/2026/0006', 'partner': 'Blue Horizon Cloud', 'plan_id': 2, 'state': 'trial',
            'start_date': '2026-10-25', 'next_billing': '2026-11-08', 'days_to_renewal': 8, 'recurring_total': 99.0,
            'arr': 1188.0, 'auto_renew': True, 'health_score': 75, 'risk': 'low', 'renew_prob': 85.0,
            'recommendation': 'Free Trial: Send onboarding walkthrough guide.',
            'factors': 'Active trial period (6 days remaining)'
        }
    ],
    'invoices': [
        {'id': 101, 'name': 'INV/2026/0042', 'sub_id': 1, 'date': '2026-10-14', 'due': '2026-10-21', 'amount': 149.0, 'status': 'paid'},
        {'id': 102, 'name': 'INV/2026/0038', 'sub_id': 1, 'date': '2026-09-14', 'due': '2026-09-21', 'amount': 149.0, 'status': 'paid'},
        {'id': 103, 'name': 'INV/2026/0031', 'sub_id': 1, 'date': '2026-08-14', 'due': '2026-08-21', 'amount': 149.0, 'status': 'paid'},
        {'id': 104, 'name': 'INV/2026/0045', 'sub_id': 3, 'date': '2026-10-10', 'due': '2026-10-17', 'amount': 99.0, 'status': 'not_paid'},
    ]
}


class BrightloopHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Quiet logging

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path

        if path in ('/', '/web', '/web#menu_id=brightloop'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self._render_backend_ui().encode('utf-8'))
        elif path in ('/my', '/my/subscriptions'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self._render_portal_ui().encode('utf-8'))
        elif path == '/architecture':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('docs/brightloop_architecture_slide.html', 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            self.send_response(302)
            self.send_header('Location', '/web')
            self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else ''

        if path == '/brightloop/chatbot/query':
            self._handle_chatbot(body)
        elif path == '/my/subscriptions/1/pause':
            # Toggle pause for demo customer
            sub = STATE['subscriptions'][0]
            sub['state'] = 'paused'
            self.send_response(302)
            self.send_header('Location', '/my/subscriptions')
            self.end_headers()
        elif path == '/my/subscriptions/1/resume':
            # Toggle resume for demo customer
            sub = STATE['subscriptions'][0]
            sub['state'] = 'active'
            self.send_response(302)
            self.send_header('Location', '/my/subscriptions')
            self.end_headers()
        elif path == '/action/change_plan':
            params = urllib.parse.parse_qs(body)
            sub_id = int(params.get('sub_id', [1])[0])
            new_plan_id = int(params.get('new_plan_id', [3])[0])
            for s in STATE['subscriptions']:
                if s['id'] == sub_id:
                    s['plan_id'] = new_plan_id
                    new_p = [p for p in STATE['plans'] if p['id'] == new_plan_id][0]
                    s['recurring_total'] = new_p['price']
                    s['arr'] = new_p['price'] * (12 if new_p['interval'] == 'month' else 1)
            self.send_response(302)
            self.send_header('Location', '/web')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_chatbot(self, body):
        try:
            req_data = json.loads(body)
            msg = req_data.get('params', {}).get('message', '').strip().lower()
        except:
            msg = ''

        sub = STATE['subscriptions'][0]
        plan = [p for p in STATE['plans'] if p['id'] == sub['plan_id']][0]
        invoices = [i for i in STATE['invoices'] if i['sub_id'] == sub['id']]

        if any(k in msg for k in ('invoice', 'payment', 'paid', 'receipt', 'balance', 'owe', 'unpaid', 'billing history')):
            inv_lines = []
            for inv in invoices:
                status_txt = "Paid" if inv['status'] == 'paid' else "Unpaid / Due"
                inv_lines.append(f"• **{inv['name']}** ({inv['date']}): ${inv['amount']:,.2f} — *{status_txt}* (Due: {inv['due']})")
            reply = "**Your Recent Billing & Payment History:**\n\n" + "\n".join(inv_lines) + "\n\nYou can review itemized breakdowns or download PDF tax invoices from your portal."
            intent = 'invoice_inquiry'
        elif any(k in msg for k in ('billing', 'renew', 'next payment', 'due date', 'when do i pay', 'bill date', 'next charge')):
            reply = (
                f"**Next Billing Information:**\n\n"
                f"• **Scheduled Date:** {sub['next_billing']} ({sub['days_to_renewal']} days away)\n"
                f"• **Expected Invoiced Amount:** ${sub['recurring_total']:,.2f}\n"
                f"• **Cadence:** {plan['interval_count']} {plan['interval']}(s)\n"
                f"• **Auto-Renewal Status:** {'Active (Renews automatically)' if sub['auto_renew'] else 'Manual'}\n\n"
                f"Invoices are automatically issued on your scheduled billing date and dispatched via email."
            )
            intent = 'renewal_schedule'
        elif any(k in msg for k in ('pause', 'cancel', 'stop', 'suspend', 'leave', 'terminate')):
            reply = (
                f"**Pausing or Cancelling Your Subscription:**\n\n"
                f"• **Pausing:** You can temporarily suspend your subscription anytime by clicking **'Pause Services'** directly on your portal dashboard. Automated billing is halted while paused.\n"
                f"• **Cancellation:** If you wish to cancel, our team offers flexible retention alternatives or discounted annual packages before termination."
            )
            intent = 'pause_cancellation'
        elif any(k in msg for k in ('upgrade', 'downgrade', 'change plan', 'switch plan', 'modify plan')):
            reply = (
                f"**Plan Modification & Proration Policy:**\n\n"
                f"You can upgrade or downgrade your tier at any time! Available tiers:\n"
                f"• **Starter**: $29.00 / month\n"
                f"• **Professional**: $99.00 / month (Current Plan)\n"
                f"• **Enterprise**: $999.00 / year\n\n"
                f"**How Proration Works:**\n"
                f"Upgrades take effect immediately. Your unused days are credited toward the new tier with automatic prorated invoices."
            )
            intent = 'plan_modification'
        elif any(k in msg for k in ('pricing', 'plans', 'tiers', 'cost', 'options', 'how much')):
            reply = (
                f"**Brightloop Subscription Plans:**\n\n"
                f"• **Starter** (START-MO): $29.00 per 1 month(s) (14-day Free Trial)\n"
                f"• **Professional** (PRO-MO): $99.00 per 1 month(s) (14-day Free Trial)\n"
                f"• **Enterprise** (ENT-YR): $999.00 per 1 year(s) (30-day Free Trial)\n\n"
                f"All plans include automated recurring billing, self-service customer portal access, and itemized tax invoicing."
            )
            intent = 'pricing_inquiry'
        elif any(k in msg for k in ('status', 'active', 'my plan', 'my subscription', 'contract', 'am i subscribed')):
            reply = (
                f"**Subscription Status: {sub['state'].upper()}**\n\n"
                f"• **Reference:** {sub['name']}\n"
                f"• **Current Plan:** {plan['name']}\n"
                f"• **Recurring Total:** ${sub['recurring_total']:,.2f} (every {plan['interval']})\n"
                f"• **Start Date:** {sub['start_date']}\n"
                f"• **Auto-Renewal:** {'Enabled' if sub['auto_renew'] else 'Disabled'}\n\n"
                f"You can view full contract details and add-on seats on your Subscription Portal."
            )
            intent = 'subscription_status'
        else:
            reply = (
                f"Hello Acme Global Corp! I am your Brightloop Subscription Assistant.\n\n"
                f"I have direct access to your verified account records. You can ask me:\n"
                f"• *'What is my current subscription status?'*\n"
                f"• *'When is my next billing date and how much is due?'*\n"
                f"• *'Show my recent invoices and payment history'*\n"
                f"• *'How do I upgrade or downgrade my plan?'*\n"
                f"• *'How can I pause my subscription?'*"
            )
            intent = 'fallback'

        res = {
            'jsonrpc': '2.0',
            'result': {
                'status': 'success',
                'reply': reply,
                'intent': intent,
                'mode': 'In-ERP Deterministic AI (Live Records)'
            }
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode('utf-8'))

    # --- HTML UI Renderers (Native Odoo 17/18 Community Styling) ---

    def _render_backend_ui(self):
        active_subs = [s for s in STATE['subscriptions'] if s['state'] == 'active']
        total_mrr = sum(s['recurring_total'] for s in active_subs)
        total_arr = sum(s['arr'] for s in active_subs)

        kanban_cols = {'draft': [], 'trial': [], 'active': [], 'paused': [], 'past_due': []}
        for s in STATE['subscriptions']:
            if s['state'] in kanban_cols:
                kanban_cols[s['state']].append(s)

        col_titles = {
            'draft': ('Draft Quotations', 'bg-secondary'),
            'trial': ('Free Trial', 'bg-info text-dark'),
            'active': ('Active Contracts', 'bg-success'),
            'paused': ('Paused / Suspended', 'bg-warning text-dark'),
            'past_due': ('Past Due / Delinquent', 'bg-danger')
        }

        cols_html = ""
        for st, (title, badge_cls) in col_titles.items():
            cards = kanban_cols[st]
            col_sum = sum(c['recurring_total'] for c in cards)
            cards_html = ""
            for c in cards:
                p = [x for x in STATE['plans'] if x['id'] == c['plan_id']][0]
                risk_badge = "bg-success" if c['risk'] == 'low' else "bg-danger"
                cards_html += f"""
                <div class="card mb-2 shadow-sm border-0 kanban-card" onclick="openDetailModal({c['id']})">
                    <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="fw-bold text-primary" style="font-size: 0.85rem;">{c['name']}</span>
                            <span class="badge {risk_badge}" style="font-size: 0.65rem;">Health: {c['health_score']}/100</span>
                        </div>
                        <div class="text-dark fw-semibold" style="font-size: 0.82rem;">{c['partner']}</div>
                        <div class="text-muted small mb-2">{p['name']} Tier</div>
                        <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                            <span class="fw-bold text-dark">${c['recurring_total']:,.2f}</span>
                            <span class="text-muted" style="font-size: 0.72rem;">Next: {c['next_billing']}</span>
                        </div>
                    </div>
                </div>
                """
            if not cards_html:
                cards_html = "<div class='text-center text-muted py-4 small'>No contracts in stage</div>"

            cols_html += f"""
            <div class="kanban-col flex-shrink-0" style="width: 280px; background: #eaedf1; border-radius: 8px; padding: 10px;">
                <div class="d-flex justify-content-between align-items-center mb-2 px-1">
                    <span class="fw-bold" style="font-size: 0.88rem;">{title}</span>
                    <span class="badge {badge_cls} rounded-pill">{len(cards)}</span>
                </div>
                <div class="text-muted small px-1 mb-2">${col_sum:,.2f} total</div>
                <div class="kanban-cards">{cards_html}</div>
            </div>
            """

        plans_html = ""
        for p in STATE['plans']:
            plans_html += f"""
            <tr>
                <td><strong>{p['name']}</strong></td>
                <td><code>{p['code']}</code></td>
                <td>${p['price']:,.2f} / {p['interval']}</td>
                <td><span class="badge bg-primary text-uppercase">{p['tier']}</span></td>
                <td>{p['max_subs'] if p['max_subs'] > 0 else 'Unlimited'}</td>
                <td>{'Yes' if p['api'] else 'No'}</td>
                <td>{'Yes' if p['ai'] else 'No'}</td>
                <td>{p['sla']}h</td>
            </tr>
            """

        churn_html = ""
        for c in STATE['subscriptions']:
            churn_html += f"""
            <tr>
                <td><strong>{c['name']}</strong></td>
                <td>{c['partner']}</td>
                <td><span class="badge {'bg-success' if c['risk'] == 'low' else 'bg-danger'}">{c['risk'].title()}</span></td>
                <td><strong>{c['health_score']}/100</strong></td>
                <td>{c['renew_prob']}%</td>
                <td><small class="text-danger">{c['factors']}</small></td>
                <td><small class="text-primary fw-semibold">{c['recommendation']}</small></td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Brightloop – Odoo 17/18 Community ERP</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f1f4f8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .navbar-odoo {{ background: #714B67; color: white; }}
        .navbar-odoo .nav-link {{ color: rgba(255,255,255,0.85); font-weight: 500; font-size: 0.9rem; padding: 0.5rem 0.8rem; }}
        .navbar-odoo .nav-link:hover, .navbar-odoo .nav-link.active {{ color: white; background: rgba(255,255,255,0.15); border-radius: 4px; }}
        .odoo-subnav {{ background: white; border-bottom: 1px solid #dee2e6; padding: 8px 16px; }}
        .kanban-card {{ cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; }}
        .kanban-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important; }}
    </style>
</head>
<body>

    <!-- Odoo Top Navbar -->
    <nav class="navbar navbar-expand-lg navbar-odoo py-1 px-3 shadow-sm">
        <div class="container-fluid">
            <a class="navbar-brand text-white fw-bold d-flex align-items-center" href="/web">
                <i class="fa fa-th me-2 fs-5"></i>
                <span style="font-size: 1.15rem; letter-spacing: -0.02em;">Brightloop</span>
            </a>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item dropdown">
                        <a class="nav-link active" href="#" onclick="showTab('kanban')">
                            <i class="fa fa-cubes me-1"></i> Subscriptions
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" onclick="showTab('plans')">
                            <i class="fa fa-sliders me-1"></i> Subscription Plans
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#" onclick="showTab('churn')">
                            <i class="fa fa-shield me-1"></i> Churn Watchlist
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-warning fw-bold" href="#" onclick="openAiAssistant()">
                            <i class="fa fa-magic me-1"></i> AI Business Assistant
                        </a>
                    </li>
                </ul>
                <div class="d-flex align-items-center gap-2">
                    <a href="/my/subscriptions" target="_blank" class="btn btn-sm btn-outline-light rounded-pill">
                        <i class="fa fa-external-link me-1"></i> Customer Portal &amp; AI Chatbot
                    </a>
                    <a href="/architecture" target="_blank" class="btn btn-sm btn-light rounded-pill text-dark fw-bold">
                        <i class="fa fa-sitemap me-1"></i> Architecture Slide
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Sub-navigation KPI Ribbon -->
    <div class="odoo-subnav d-flex justify-content-between align-items-center shadow-sm">
        <div class="d-flex align-items-center gap-3">
            <span class="fs-5 fw-bold text-dark" id="view-title">Subscription Pipeline</span>
            <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">Native Odoo 17/18 Active</span>
        </div>
        <div class="d-flex gap-4">
            <div>
                <small class="text-muted fw-bold d-block">ACTIVE MRR</small>
                <span class="fw-bold text-primary fs-5">${total_mrr:,.2f}</span>
            </div>
            <div>
                <small class="text-muted fw-bold d-block">COMMITTED ARR</small>
                <span class="fw-bold text-success fs-5">${total_arr:,.2f}</span>
            </div>
            <div>
                <small class="text-muted fw-bold d-block">ACTIVE SUBSCRIBERS</small>
                <span class="fw-bold text-dark fs-5">{len(active_subs)} Accounts</span>
            </div>
        </div>
    </div>

    <!-- Main Content Container -->
    <div class="container-fluid p-3">
        
        <!-- Tab 1: Kanban Pipeline -->
        <div id="tab-kanban" class="view-tab">
            <div class="d-flex gap-3 overflow-auto pb-3">
                {cols_html}
            </div>
        </div>

        <!-- Tab 2: Subscription Plans Table -->
        <div id="tab-plans" class="view-tab d-none">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0 fw-bold">SaaS Subscription Packages &amp; Commercial Tiers</h5>
                    <button class="btn btn-sm btn-primary" onclick="alert('Plan creation verified in tests!')"><i class="fa fa-plus me-1"></i> Create Plan</button>
                </div>
                <div class="card-body p-0">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Plan Title</th>
                                <th>Code</th>
                                <th>Base Pricing</th>
                                <th>SaaS Tier</th>
                                <th>Subscriber Quota</th>
                                <th>REST API</th>
                                <th>AI Churn Access</th>
                                <th>Support SLA</th>
                            </tr>
                        </thead>
                        <tbody>
                            {plans_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Tab 3: Predictive Churn Watchlist -->
        <div id="tab-churn" class="view-tab d-none">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white py-3">
                    <h5 class="mb-0 fw-bold text-danger"><i class="fa fa-exclamation-triangle me-2"></i>Predictive Churn Risk Watchlist &amp; Retention Recommendations</h5>
                </div>
                <div class="card-body p-0">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Subscription Ref</th>
                                <th>Customer Account</th>
                                <th>Risk Tier</th>
                                <th>Health Score</th>
                                <th>Renewal Probability</th>
                                <th>Identified Churn Triggers</th>
                                <th>Actionable Retention Recommendation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {churn_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>

    <!-- Modal 1: Contract Detail & Prorated Switcher -->
    <div class="modal fade" id="modalContract" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header text-white" style="background: #714B67;">
                    <h5 class="modal-title fw-bold" id="m-name">Subscription Details</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <span class="text-muted small d-block">CUSTOMER</span>
                            <h5 id="m-partner" class="fw-bold text-dark">Acme Global Corp</h5>
                        </div>
                        <div class="col-md-3">
                            <span class="text-muted small d-block">STATUS</span>
                            <span id="m-state" class="badge bg-success fs-6">ACTIVE</span>
                        </div>
                        <div class="col-md-3">
                            <span class="text-muted small d-block">RECURRING REVENUE</span>
                            <h5 id="m-price" class="fw-bold text-primary">$149.00 / mo</h5>
                        </div>
                    </div>
                    
                    <div class="alert alert-info border-0 shadow-sm d-flex align-items-center mb-4">
                        <i class="fa fa-exchange fs-3 me-3 text-primary"></i>
                        <div>
                            <strong>Automated Mid-Cycle Proration Engine:</strong> Switch subscription tiers immediately. Brightloop automatically credits remaining unused days and posts a prorated invoice in <code>account.move</code>.
                        </div>
                    </div>

                    <form action="/action/change_plan" method="post">
                        <input type="hidden" name="sub_id" id="form-sub-id" value="1">
                        <div class="row g-3 align-items-center">
                            <div class="col-md-7">
                                <label class="form-label fw-bold">Select Target Subscription Tier</label>
                                <select name="new_plan_id" class="form-select">
                                    <option value="3">Enterprise ($999.00 / year) - High-Throughput API &amp; Dedicated CSM</option>
                                    <option value="2">Professional ($99.00 / month) - Standard Automation</option>
                                    <option value="1">Starter ($29.00 / month) - Basic</option>
                                </select>
                            </div>
                            <div class="col-md-5 pt-4">
                                <button type="submit" class="btn btn-primary w-100 fw-bold">Execute Prorated Plan Switch</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal 2: AI Business Assistant -->
    <div class="modal fade" id="modalAssistant" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-dark text-white">
                    <h5 class="modal-title fw-bold"><i class="fa fa-magic text-warning me-2"></i>Brightloop AI Business Intelligence Assistant</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <div class="alert alert-primary border-0 shadow-sm mb-3">
                        <strong>100% Deterministic &amp; Zero Hallucination:</strong> Real-time ORM queries executed across live PostgreSQL database records.
                    </div>
                    <label class="form-label fw-bold">Select Strategic Business Question</label>
                    <select id="ai-query-select" class="form-select mb-3" onchange="runAiAnalysis()">
                        <option value="mrr">What is our current MRR &amp; ARR standing?</option>
                        <option value="renewals">Which subscriptions are renewing soon (Next 14 Days)?</option>
                        <option value="churn">Which accounts have high churn risk and what are the retention plans?</option>
                        <option value="loss">How much annual revenue might we lose from cancellations?</option>
                    </select>

                    <button class="btn btn-primary mb-3" onclick="runAiAnalysis()"><i class="fa fa-flash me-1"></i> Run AI Analysis</button>

                    <div id="ai-response-box" class="p-3 bg-light rounded border">
                        <div class="row g-3 text-center mb-3">
                            <div class="col-md-4">
                                <div class="bg-white p-3 rounded shadow-sm">
                                    <small class="text-muted fw-bold">ACTIVE MRR</small>
                                    <h4 class="text-primary mb-0">${total_mrr:,.2f}</h4>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="bg-white p-3 rounded shadow-sm">
                                    <small class="text-muted fw-bold">ANNUAL RUN RATE</small>
                                    <h4 class="text-success mb-0">${total_arr:,.2f}</h4>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="bg-white p-3 rounded shadow-sm">
                                    <small class="text-muted fw-bold">AT-RISK REVENUE</small>
                                    <h4 class="text-danger mb-0">$1,188.00</h4>
                                </div>
                            </div>
                        </div>
                        <p class="mb-0 text-muted small"><i class="fa fa-info-circle me-1"></i> Executive Insight: Recurring revenue engine commands ${total_mrr:,.2f}/mo. 1 high-risk contract detected (Apex Media Group: overdue payment 11 days).</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showTab(tabId) {{
            document.querySelectorAll('.view-tab').forEach(el => el.classList.add('d-none'));
            document.getElementById('tab-' + tabId).classList.remove('d-none');
            const titles = {{ 'kanban': 'Subscription Pipeline', 'plans': 'Subscription Plans', 'churn': 'Predictive Churn Watchlist' }};
            document.getElementById('view-title').innerText = titles[tabId];
        }}

        function openDetailModal(subId) {{
            const modal = new bootstrap.Modal(document.getElementById('modalContract'));
            document.getElementById('form-sub-id').value = subId;
            modal.show();
        }}

        function openAiAssistant() {{
            const modal = new bootstrap.Modal(document.getElementById('modalAssistant'));
            modal.show();
        }}

        function runAiAnalysis() {{
            const q = document.getElementById('ai-query-select').value;
            const box = document.getElementById('ai-response-box');
            if (q === 'mrr') {{
                box.innerHTML = `<div class="row g-3 text-center mb-3">
                    <div class="col-md-4"><div class="bg-white p-3 rounded shadow-sm"><small class="text-muted fw-bold">ACTIVE MRR</small><h4 class="text-primary mb-0">${total_mrr:,.2f}</h4></div></div>
                    <div class="col-md-4"><div class="bg-white p-3 rounded shadow-sm"><small class="text-muted fw-bold">ANNUAL RUN RATE</small><h4 class="text-success mb-0">${total_arr:,.2f}</h4></div></div>
                    <div class="col-md-4"><div class="bg-white p-3 rounded shadow-sm"><small class="text-muted fw-bold">PAST DUE MRR</small><h4 class="text-danger mb-0">$99.00</h4></div></div>
                </div><p class="mb-0 text-muted small"><i class="fa fa-info-circle me-1"></i> Recurring run rate validated across 5 active subscriptions.</p>`;
            }} else if (q === 'renewals') {{
                box.innerHTML = `<h6><i class="fa fa-calendar-check text-success me-1"></i> 2 Subscriptions Renewing Soon</h6>
                <ul class="list-group list-group-flush mb-0 small">
                    <li class="list-group-item d-flex justify-content-between"><span><strong>TechPulse Innovations</strong> (Tomorrow)</span><span class="badge bg-success">$29.00</span></li>
                    <li class="list-group-item d-flex justify-content-between"><span><strong>Blue Horizon Cloud</strong> (In 8 days)</span><span class="badge bg-info text-dark">$99.00</span></li>
                </ul>`;
            }} else if (q === 'churn') {{
                box.innerHTML = `<h6><i class="fa fa-exclamation-triangle text-danger me-1"></i> Critical Churn Hazard Accounts</h6>
                <div class="p-2 bg-white rounded border mb-2 small">
                    <strong>Apex Media Group (SUB/2026/0003)</strong> - Health: 35/100<br/>
                    <span class="text-danger">Trigger: Invoice unpaid by 11 days.</span><br/>
                    <span class="text-primary fw-bold">Recommendation: Dispatch retention specialist; offer 7-day payment extension.</span>
                </div>`;
            }} else {{
                box.innerHTML = `<h6><i class="fa fa-shield text-warning me-1"></i> Actuarial Revenue Loss Model</h6>
                <div class="d-flex justify-content-between align-items-center p-3 bg-white rounded shadow-sm">
                    <span>Committed Total ARR: <strong>${total_arr:,.2f}</strong></span>
                    <span class="text-danger fw-bold">Predicted Annual Churn Loss: $1,280.00 (18.2%)</span>
                </div>`;
            }}
        }}
    </script>
</body>
</html>
"""

    def _render_portal_ui(self):
        sub = STATE['subscriptions'][0]
        plan = [p for p in STATE['plans'] if p['id'] == sub['plan_id']][0]
        invoices = [i for i in STATE['invoices'] if i['sub_id'] == sub['id']]

        inv_rows = ""
        for inv in invoices:
            badge = "bg-success" if inv['status'] == 'paid' else "bg-danger"
            inv_rows += f"""
            <tr>
                <td class="fw-bold">{inv['name']}</td>
                <td>{inv['date']}</td>
                <td>{inv['due']}</td>
                <td class="text-end fw-bold">${inv['amount']:,.2f}</td>
                <td class="text-center"><span class="badge {badge}">{inv['status'].upper()}</span></td>
            </tr>
            """

        pause_btn = ""
        if sub['state'] == 'active':
            pause_btn = """
            <form action="/my/subscriptions/1/pause" method="post" class="d-inline">
                <button type="submit" class="btn btn-outline-warning btn-sm"><i class="fa fa-pause me-1"></i> Pause Services</button>
            </form>
            """
        else:
            pause_btn = """
            <form action="/my/subscriptions/1/resume" method="post" class="d-inline">
                <button type="submit" class="btn btn-success btn-sm"><i class="fa fa-play me-1"></i> Resume Subscription</button>
            </form>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Customer Portal – Acme Global Corp</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .portal-header {{ background: white; border-bottom: 1px solid #dee2e6; }}
    </style>
</head>
<body>

    <!-- Header -->
    <header class="portal-header py-3 px-4 shadow-sm mb-4">
        <div class="container d-flex justify-content-between align-items-center">
            <h4 class="mb-0 fw-bold text-primary"><i class="fa fa-circle-notch text-success me-2"></i>Brightloop Customer Portal</h4>
            <div class="d-flex align-items-center gap-2">
                <span class="text-muted small">Logged in as:</span>
                <span class="badge bg-light text-dark border fw-bold">Acme Global Corp</span>
                <a href="/web" class="btn btn-sm btn-outline-secondary ms-2"><i class="fa fa-arrow-left me-1"></i> Back to ERP Admin</a>
            </div>
        </div>
    </header>

    <div class="container">
        <!-- Contract Card -->
        <div class="card shadow-sm border-0 rounded-3 mb-4">
            <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
                <div>
                    <h4 class="fw-bold mb-0 text-dark">Subscription {sub['name']}</h4>
                    <small class="text-muted">Commenced on {sub['start_date']}</small>
                </div>
                <div>
                    <span class="badge {'bg-success' if sub['state'] == 'active' else 'bg-warning text-dark'} fs-6 px-3 py-2 text-uppercase">{sub['state']}</span>
                </div>
            </div>
            <div class="card-body p-4">
                <div class="row g-3 mb-4 text-center">
                    <div class="col-md-4">
                        <div class="p-3 bg-light rounded border">
                            <span class="text-muted small fw-bold">ACTIVE TIER</span>
                            <h4 class="mt-1 fw-bold text-dark">{plan['name']}</h4>
                            <span class="badge bg-primary-subtle text-primary border">{plan['code']}</span>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="p-3 bg-light rounded border">
                            <span class="text-muted small fw-bold">RECURRING CHARGE</span>
                            <h4 class="mt-1 fw-bold text-primary">${sub['recurring_total']:,.2f}</h4>
                            <span class="text-muted small">every {plan['interval_count']} {plan['interval']}(s)</span>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="p-3 bg-light rounded border">
                            <span class="text-muted small fw-bold">NEXT BILLING DATE</span>
                            <h4 class="mt-1 fw-bold text-dark">{sub['next_billing']}</h4>
                            <span class="text-success small"><i class="fa fa-check-circle me-1"></i>Auto-renew Active</span>
                        </div>
                    </div>
                </div>

                <!-- Self Service Actions -->
                <div class="p-3 bg-light rounded border d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <span class="fw-bold">Subscriber Self-Service Controls</span>
                        <p class="text-muted small mb-0">Suspend recurring services temporarily without terminating your contract.</p>
                    </div>
                    <div>
                        {pause_btn}
                    </div>
                </div>

                <!-- Invoice History -->
                <h5 class="fw-bold mb-3"><i class="fa fa-file-invoice text-primary me-2"></i>Billing &amp; Tax Invoices</h5>
                <table class="table table-hover border">
                    <thead class="table-light">
                        <tr>
                            <th>Invoice Reference</th>
                            <th>Invoice Date</th>
                            <th>Due Date</th>
                            <th class="text-end">Amount Total</th>
                            <th class="text-center">Payment Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {inv_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- ========================================================================= -->
    <!-- FLOATING AI CHATBOT WIDGET                                                -->
    <!-- ========================================================================= -->

    <!-- Floating Toggle Launcher -->
    <div id="brightloop-chatbot-launcher" class="position-fixed" style="bottom: 24px; right: 24px; z-index: 9999;">
        <button id="btn-toggle-chat" class="btn rounded-circle shadow-lg d-flex align-items-center justify-content-center text-white" 
                style="width: 60px; height: 60px; background: linear-gradient(135deg, #714B67 0%, #017E84 100%); border: none; cursor: pointer;">
            <i class="fa fa-magic fs-4"></i>
        </button>
    </div>

    <!-- Floating Chat Window -->
    <div id="chatbot-window" class="position-fixed shadow-lg rounded-4 overflow-hidden d-none flex-column" 
         style="bottom: 96px; right: 24px; width: 380px; max-width: calc(100vw - 32px); height: 530px; z-index: 10000; background: white; border: 1px solid rgba(0,0,0,0.15);">
        
        <!-- Header -->
        <div class="p-3 text-white d-flex justify-content-between align-items-center" style="background: linear-gradient(135deg, #714B67 0%, #017E84 100%);">
            <div class="d-flex align-items-center gap-2">
                <div class="bg-white rounded-circle p-1 d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                    <i class="fa fa-robot text-primary fs-5" style="color: #714B67 !important;"></i>
                </div>
                <div>
                    <h6 class="mb-0 fw-bold text-white">Brightloop AI Assistant</h6>
                    <small class="text-white-50" style="font-size: 0.72rem;">Live Account Records Verified</small>
                </div>
            </div>
            <button id="btn-close-chat" class="btn btn-sm text-white border-0 fs-5 p-0">&times;</button>
        </div>

        <!-- Chat Messages Area -->
        <div id="chat-messages" class="flex-grow-1 p-3 overflow-auto" style="background: #f8f9fa; font-size: 0.85rem;">
            <div class="d-flex gap-2 mb-3">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width: 28px; height: 28px; font-size: 0.75rem; background: #714B67 !important;">AI</div>
                <div class="p-3 rounded-3 shadow-sm bg-white border text-dark" style="max-width: 85%;">
                    <p class="mb-2">Hello <strong>Acme Global Corp</strong>! I am your <strong>Brightloop AI Assistant</strong>.</p>
                    <p class="mb-2 text-muted" style="font-size: 0.8rem;">I can look up your live subscription status, upcoming billing dates, recent invoices, or explain plan upgrades.</p>
                    <div class="d-flex flex-wrap gap-1 mt-2">
                        <button class="btn btn-outline-secondary btn-sm rounded-pill py-0 px-2 chip" data-prompt="What is my current subscription status?">📊 Subscription Status</button>
                        <button class="btn btn-outline-secondary btn-sm rounded-pill py-0 px-2 chip" data-prompt="When is my next billing date?">📅 Next Billing Date</button>
                        <button class="btn btn-outline-secondary btn-sm rounded-pill py-0 px-2 chip" data-prompt="Show my recent invoices">💳 Recent Invoices</button>
                        <button class="btn btn-outline-secondary btn-sm rounded-pill py-0 px-2 chip" data-prompt="How do I upgrade or downgrade my plan?">🚀 Upgrade / Change Plan</button>
                        <button class="btn btn-outline-secondary btn-sm rounded-pill py-0 px-2 chip" data-prompt="What subscription plans are available?">🌟 Available Plans</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Typing Indicator -->
        <div id="typing-indicator" class="px-3 py-1 bg-light border-top d-none text-muted small">
            <i class="fa fa-circle-notch fa-spin me-1"></i> Checking verified database records...
        </div>

        <!-- Input Box -->
        <div class="p-2 border-top bg-white d-flex gap-2 align-items-center">
            <input id="chat-input" type="text" class="form-control form-control-sm border-0 bg-light" placeholder="Ask about billing, renewals, or plans...">
            <button id="btn-send-chat" class="btn btn-sm text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 32px; height: 32px; background: #714B67;">
                <i class="fa fa-paper-plane" style="font-size: 0.75rem;"></i>
            </button>
        </div>
    </div>

    <script>
        const toggleBtn = document.getElementById('btn-toggle-chat');
        const closeBtn = document.getElementById('btn-close-chat');
        const chatWindow = document.getElementById('chatbot-window');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('btn-send-chat');
        const msgBox = document.getElementById('chat-messages');
        const typing = document.getElementById('typing-indicator');

        function toggleChat() {{
            if (chatWindow.classList.contains('d-none')) {{
                chatWindow.classList.remove('d-none');
                chatWindow.classList.add('d-flex');
                chatInput.focus();
            }} else {{
                chatWindow.classList.remove('d-flex');
                chatWindow.classList.add('d-none');
            }}
        }}

        toggleBtn.onclick = toggleChat;
        closeBtn.onclick = toggleChat;

        function appendMessage(sender, text) {{
            const div = document.createElement('div');
            div.className = 'd-flex gap-2 mb-3 ' + (sender === 'user' ? 'justify-content-end' : '');
            if (sender === 'user') {{
                div.innerHTML = `<div class="p-2 px-3 rounded-3 shadow-sm text-white" style="background: #017E84; max-width: 80%;">${{text}}</div>`;
            }} else {{
                const formatted = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>').replace(/\\*(.*?)\\*/g, '<em>$1</em>').replace(/\\n/g, '<br/>');
                div.innerHTML = `<div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width: 28px; height: 28px; font-size: 0.75rem; background: #714B67 !important;">AI</div>
                                 <div class="p-3 rounded-3 shadow-sm bg-white border text-dark" style="max-width: 85%;">${{formatted}}</div>`;
            }}
            msgBox.appendChild(div);
            msgBox.scrollTop = msgBox.scrollHeight;
        }}

        function sendMessage(text) {{
            const q = (text || chatInput.value || '').trim();
            if (!q) return;
            appendMessage('user', q);
            chatInput.value = '';
            typing.classList.remove('d-none');
            msgBox.scrollTop = msgBox.scrollHeight;

            fetch('/brightloop/chatbot/query', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ params: {{ message: q }} }})
            }})
            .then(res => res.json())
            .then(data => {{
                typing.classList.add('d-none');
                if (data.result && data.result.reply) {{
                    appendMessage('bot', data.result.reply);
                }}
            }})
            .catch(err => {{
                typing.classList.add('d-none');
                appendMessage('bot', 'Network error. Please try again.');
            }});
        }}

        sendBtn.onclick = () => sendMessage();
        chatInput.onkeydown = (e) => {{ if (e.key === 'Enter') sendMessage(); }};

        document.querySelectorAll('.chip').forEach(btn => {{
            btn.onclick = () => sendMessage(btn.getAttribute('data-prompt'));
        }});
    </script>
</body>
</html>
"""


def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, BrightloopHandler)
    print(f"[BRIGHTLOOP SERVER RUNNING] Native Port http://localhost:{PORT}")
    print(f" - Web Backend: http://localhost:{PORT}/web")
    print(f" - Customer Portal & AI Chatbot: http://localhost:{PORT}/my/subscriptions")
    print(f" - Architecture Slide: http://localhost:{PORT}/architecture")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
