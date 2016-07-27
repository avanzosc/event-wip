# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _
from datetime import datetime
import calendar


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    create_account = fields.Boolean(
        string='Show create account', default=False)

    @api.onchange('partner')
    def onchange_partner(self):
        self.create_account = False
        if self.registration and self.partner:
            self.create_account = True
            sale_order = self.registration.event_id.sale_order
            if (self.partner.employee or self.registration.analytic_account or
                    sale_order.project_id.recurring_invoices):
                self.create_account = False

    @api.multi
    def action_append(self):
        self.ensure_one()
        event_obj = self.env['event.event']
        result = super(WizEventAppendAssistant, self).action_append()
        if self.create_account and not self.registration:
            for event in event_obj.browse(self.env.context.get('active_ids')):
                registration = event.registration_ids.filtered(
                    lambda x: x.partner_id.id == self.partner.id and not
                    x.analytic_account)
                if registration:
                    self._create_account_for_not_employee_from_wizard(
                        event, registration)
        if self.create_account and self.registration:
            self._create_account_for_not_employee_from_wizard(
                self.registration.event_id, self.registration)
        return result

    def _create_account_for_not_employee_from_wizard(
            self, event, registration):
        account_obj = self.env['account.analytic.account']
        analytic_invoice_line_obj = self.env['account.analytic.invoice.line']
        vals = self._prepare_data_for_account_not_employee(event, registration)
        new_account = account_obj.create(vals)
        registration.analytic_account = new_account.id
        for ticket in event.event_ticket_ids:
            line_vals = {'analytic_account_id': new_account.id,
                         'name': (ticket.sale_line.name or
                                  ticket.product_id.name),
                         'price_unit': ticket.price,
                         'price_subtotal': ticket.sale_line.price_subtotal,
                         'product_id': ticket.product_id.id,
                         'quantity': ticket.sale_line.product_uom_qty,
                         'uom_id': (ticket.sale_line.product_uom.id or
                                    ticket.product_id.uom_id.id)}
            analytic_invoice_line_obj.create(line_vals)

    def _prepare_data_for_account_not_employee(self, event, registration):
        event_obj = self.env['event.event']
        today = datetime.strptime(
            fields.Date.context_today(self), '%Y-%m-%d').date()
        recurrring_next_date = "%s-%s-%s" % (
            today.year, today.month,
            calendar.monthrange(today.year, today.month)[1])
        code = self.env['ir.sequence'].get(
            'account.analytic.account')
        from_date = event_obj._convert_date_to_local_format_with_hour(
            registration.date_start).date()
        to_date = event_obj._convert_date_to_local_format_with_hour(
            registration.date_end).date()
        parent_id = event.project_id.analytic_account_id.id or False
        if len(event.my_task_ids) == 1:
            parent_id = event.my_task_ids[0].project_id.analytic_account_id.id
        vals = {'name': (_('Student: %s - Payer: %s') %
                         (registration.partner_id.name,
                          registration.partner_id.parent_id.name)),
                'type': 'contract',
                'date_start': from_date,
                'date': to_date,
                'parent_id': parent_id,
                'code': code,
                'partner_id': registration.partner_id.id,
                'recurring_invoices': True,
                'recurring_next_date': recurrring_next_date}
        return vals
