# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    no_employee_registration_ids = fields.One2many(
        comodel_name='event.registration', inverse_name='event_id',
        string='Registered students', readonly=False,
        states={'done': [('readonly', True)]},
        domain=[('employee', '=', False)])
    employee_registration_ids = fields.One2many(
        comodel_name='event.registration', inverse_name='event_id',
        string='Registered teachers', readonly=False,
        states={'done': [('readonly', True)]},
        domain=[('employee', '!=', False)])

    def _create_event_from_sale(self, by_task, sale, line=False):
        event = super(EventEvent, self)._create_event_from_sale(
            by_task, sale, line=line)
        if by_task:
            self._create_event_ticket(event, line)
        else:
            sale_lines = sale.order_line.filtered(
                lambda x: x.recurring_service)
            for line in sale_lines:
                self._create_event_ticket(event, line)
        return event

    def _create_event_ticket(self, event, line):
        ticket_obj = self.env['event.event.ticket']
        line.product_id.event_ok = True
        ticket_vals = {'event_id': event.id,
                       'product_id': line.product_id.id,
                       'name': line.name,
                       'price': line.price_subtotal,
                       'sale_line': line.id}
        ticket = ticket_obj.create(ticket_vals)
        line.write({'event_id': event.id,
                    'event_ticket_id': ticket.id,
                    'event_ok': True})


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.depends('event_id', 'event_id.sale_order',
                 'event_id.sale_order.project_id',
                 'event_id.sale_order.project_id.recurring_invoices')
    def _calculate_required_account(self):
        for reg in self:
            reg.required_account = True
            if (reg.employee or reg.analytic_account or
                    reg.event_id.sale_order.project_id.recurring_invoices):
                reg.required_account = False

    required_account = fields.Boolean(
        string='Required account', compute='_calculate_required_account')
    analytic_account = fields.Many2one(
        'account.analytic.account', string='Analytic account')
    employee = fields.Many2one(
        'hr.employee', string='Employee', related='partner_id.employee_id',
        store=True)

    @api.onchange('partner_id', 'partner_id.employee_id')
    def _onchange_partner(self):
        super(EventRegistration, self)._onchange_partner()
        self.employee = self.partner_id.employee_id

    @api.multi
    def registration_open(self):
        wiz_obj = self.env['wiz.event.append.assistant']
        result = super(EventRegistration, self).registration_open()
        wiz = wiz_obj.browse(result.get('res_id'))
        wiz.create_account = self.required_account
        return result


class EventEventTicket(models.Model):
    _inherit = 'event.event.ticket'

    sale_line = fields.Many2one(
        'sale.order.line', string='Sale line')
