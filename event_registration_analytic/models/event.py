# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


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
    count_teacher_registrations = fields.Integer(
        string='Teacher assistants',
        compute='_count_teacher_registrations')
    count_pickings = fields.Integer(
        string='Pickings',
        compute='_count_teacher_pickings')
    count_moves = fields.Integer(
        string='Moves',
        compute='_count_teacher_moves')

    @api.one
    @api.depends('registration_ids')
    def _count_registrations(self):
        super(EventEvent, self)._count_registrations()
        self.count_registrations = len(self.no_employee_registration_ids)

    @api.one
    @api.depends('registration_ids')
    def _count_teacher_registrations(self):
        self.count_teacher_registrations = len(self.employee_registration_ids)

    @api.one
    def _count_teacher_pickings(self):
        picking_obj = self.env['stock.picking']
        partners = self.env['res.partner']
        partners |= self.employee_registration_ids.mapped('partner_id')
        cond = [('partner_id', 'in', partners.ids)]
        pickings = picking_obj.search(cond)
        self.count_pickings = len(pickings)

    @api.one
    def _count_teacher_moves(self):
        move_obj = self.env['stock.move']
        partners = self.env['res.partner']
        partners |= self.employee_registration_ids.mapped('partner_id')
        cond = [('partner_id', 'in', partners.ids)]
        moves = move_obj.search(cond)
        self.count_moves = len(moves)

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
        ticket_obj.create(ticket_vals)

    @api.multi
    def write(self, vals):
        if (vals.get('employee_registration_ids', False) and
                vals.get('no_employee_registration_ids', False)):
            new_lines = []
            for line in vals.get('no_employee_registration_ids'):
                if line[0] != 2 and line[2] is not False:
                    new_lines.append(line)
            if new_lines:
                vals['no_employee_registration_ids'] = new_lines
            else:
                vals.pop('no_employee_registration_ids')
            new_lines = []
            for line in vals.get('employee_registration_ids'):
                if line[0] != 2 and line[2] is not False:
                    new_lines.append(line)
            if new_lines:
                vals['employee_registration_ids'] = new_lines
            else:
                vals.pop('employee_registration_ids')
        return super(EventEvent, self).write(vals)

    @api.multi
    def show_teacher_registrations(self):
        self.ensure_one()
        return {'name': _('Teacher assistants'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form,calendar,graph',
                'view_type': 'form',
                'res_model': 'event.registration',
                'domain': [('id', 'in', self.employee_registration_ids.ids)]}

    @api.multi
    def show_teacher_pickings(self):
        self.ensure_one()
        picking_obj = self.env['stock.picking']
        partners = self.env['res.partner']
        partners |= self.employee_registration_ids.mapped('partner_id')
        cond = [('partner_id', 'in', partners.ids)]
        pickings = picking_obj.search(cond)
        return {'name': _('Teachers pickings'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form,calendar',
                'view_type': 'form',
                'res_model': 'stock.picking',
                'domain': [('partner_id', 'in', pickings.ids)]}

    @api.multi
    def show_teacher_moves(self):
        move_obj = self.env['stock.move']
        partners = self.env['res.partner']
        partners |= self.employee_registration_ids.mapped('partner_id')
        cond = [('partner_id', 'in', partners.ids)]
        moves = move_obj.search(cond)
        return {'name': _('Teachers moves'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'stock.move',
                'domain': [('partner_id', 'in', moves.ids)]}


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
        comodel_name='account.analytic.account', string='Analytic account')
    employee = fields.Many2one(
        comodel_name='hr.employee', string='Employee',
        related='partner_id.employee_id', store=True)

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
        comodel_name='sale.order.line', string='Sale line')


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    employee = fields.Many2one(
        comodel_name='hr.employee', string='Employee',
        related='partner.employee_id', store=True)


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.depends('presences', 'presences.real_duration')
    def _calc_real_duration(self):
        for track in self:
            track.real_duration = 0
            if track.presences:
                presence = max(track.presences, key=lambda x: x.real_duration)
                if presence:
                    track.real_duration = presence.real_duration

    no_employee_presences = fields.One2many(
        comodel_name='event.track.presence', inverse_name='session',
        string='Student presences', readonly=False,
        domain=[('employee', '=', False)])
    employee_presences = fields.One2many(
        comodel_name='event.track.presence', inverse_name='session',
        string='Teacher presences', readonly=False,
        domain=[('employee', '!=', False)])

    @api.multi
    def write(self, vals):
        if 'no_employee_presences' in vals and 'employee_presences' in vals:
            vals.pop('presences', None)
        return super(EventTrack, self).write(vals)
