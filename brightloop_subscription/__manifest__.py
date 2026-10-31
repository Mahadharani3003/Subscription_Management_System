# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Brightloop - Subscription Management System',
    'version': '17.0.1.0.0',
    'category': 'Sales/Subscriptions',
    'summary': 'Modern, Enterprise-Grade Recurring Billing, Lifecycle, and Dunning Management',
    'description': """
Brightloop - Subscription Management System
===========================================
Built for the Odoo Kochi Hackathon, Brightloop provides an end-to-end
subscription management platform for SaaS businesses, digital services,
and recurring memberships.

Key Features:
-------------
* **Subscription Plans & Tiers**: Flexible billing intervals (Days, Months, Years), pricing, and trial periods.
* **Automated Recurring Billing**: Automated cron-based invoice generation linking directly into Odoo's native `account.move`.
* **State Machine & Lifecycle**: Full contract tracking from Draft, Free Trial, Active, Paused, Past Due to Cancellation.
* **Add-ons & Seat Metering**: Expandable subscription line items for extra seats, quotas, and modular features.
* **Dunning & Grace Periods**: Automated grace period enforcement, payment retry tracking, and churn management.
* **MRR & ARR Analytics**: Real-time normalized Monthly Recurring Revenue and Annual Recurring Revenue calculations.
* **Role-Based Security**: Complete access rules for Subscription Officers, Managers, and Portal Subscribers.
    """,
    'author': 'Brightloop Team',
    'website': 'https://brightloop.io',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'account',
        'portal',
    ],
    'data': [
        'security/brightloop_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
    ],
    'demo': [
        'demo/brightloop_demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
