# -*- coding: utf-8 -*-
# Part of Brightloop Subscription Management System.
# See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class BrightloopCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """Add subscription count badge on customer portal home page."""
        values = super()._prepare_home_portal_values(counters)
        if 'subscription_count' in counters:
            partner = request.env.user.partner_id
            sub_count = request.env['brightloop.subscription'].search_count([
                ('partner_id', 'child_of', [partner.commercial_partner_id.id])
            ])
            values['subscription_count'] = sub_count
        return values

    @http.route(['/my/subscriptions', '/my/subscriptions/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_subscriptions(self, page=1, sortby=None, filterby=None, **kw):
        """List all subscriptions belonging to the logged-in portal user."""
        Subscription = request.env['brightloop.subscription']
        partner = request.env.user.partner_id

        domain = [('partner_id', 'child_of', [partner.commercial_partner_id.id])]

        # Sorting Options
        searchbar_sortings = {
            'date': {'label': _('Next Billing Date'), 'order': 'next_billing_date asc'},
            'name': {'label': _('Reference'), 'order': 'name asc'},
            'amount': {'label': _('Recurring Amount'), 'order': 'recurring_total desc'},
        }
        if not sortby or sortby not in searchbar_sortings:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Filters
        searchbar_filters = {
            'all': {'label': _('All Subscriptions'), 'domain': []},
            'active': {'label': _('Active'), 'domain': [('state', '=', 'active')]},
            'trial': {'label': _('Free Trial'), 'domain': [('state', '=', 'trial')]},
            'past_due': {'label': _('Past Due'), 'domain': [('state', '=', 'past_due')]},
        }
        if not filterby or filterby not in searchbar_filters:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        sub_count = Subscription.search_count(domain)
        pager = portal_pager(
            url="/my/subscriptions",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=sub_count,
            page=page,
            step=10
        )

        subscriptions = Subscription.search(domain, order=order, limit=10, offset=pager['offset'])

        values = {
            'subscriptions': subscriptions,
            'page_name': 'subscription',
            'pager': pager,
            'default_url': '/my/subscriptions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        }
        return request.render('brightloop_subscription.portal_my_subscriptions', values)

    @http.route(['/my/subscriptions/<int:sub_id>'], type='http', auth='user', website=True)
    def portal_subscription_page(self, sub_id, **kw):
        """Detailed view of an individual subscription for customer self-service."""
        try:
            sub = request.env['brightloop.subscription'].browse(sub_id)
            sub.check_access_rights('read')
            sub.check_access_rule('read')
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'subscription': sub,
            'page_name': 'subscription_detail',
            'invoices': sub.invoice_ids.sudo().filtered(lambda i: i.state == 'posted'),
        }
        return request.render('brightloop_subscription.portal_subscription_page', values)

    @http.route(['/my/subscriptions/<int:sub_id>/pause'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def portal_subscription_pause(self, sub_id, **kw):
        """Self-service endpoint allowing subscriber to pause their active contract."""
        sub = request.env['brightloop.subscription'].browse(sub_id)
        if sub.exists() and sub.partner_id.id == request.env.user.partner_id.id and sub.state == 'active':
            sub.sudo().action_pause()
        return request.redirect(f'/my/subscriptions/{sub_id}')

    @http.route(['/my/subscriptions/<int:sub_id>/resume'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def portal_subscription_resume(self, sub_id, **kw):
        """Self-service endpoint allowing subscriber to resume a paused contract."""
        sub = request.env['brightloop.subscription'].browse(sub_id)
        if sub.exists() and sub.partner_id.id == request.env.user.partner_id.id and sub.state == 'paused':
            sub.sudo().action_resume()
        return request.redirect(f'/my/subscriptions/{sub_id}')
