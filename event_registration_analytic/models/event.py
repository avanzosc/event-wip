# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _


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
    count_all_registrations = fields.Integer(
        string='All assistants',
        compute='_count_registrations')
    count_teacher_registrations = fields.Integer(
        string='Teacher assistants',
        compute='_count_registrations')
    count_pickings = fields.Integer(
        string='Pickings',
        compute='_compute_count_teacher_pickings_moves')
    count_moves = fields.Integer(
        string='Moves',
        compute='_compute_count_teacher_pickings_moves')
    seats_canceled = fields.Integer(
        string='Canceled registrations', store=True, readonly=True,
        compute='_compute_seats')
    count_presences = fields.Integer(
        string='Presences',
        compute='_compute_count_presences')

    @api.multi
    @api.depends('registration_ids')
    def _count_registrations(self):
        for record in self:
            super(EventEvent, record)._count_registrations()
            record.count_registrations =\
                len(record.no_employee_registration_ids)
            record.count_all_registrations = len(record.registration_ids)
            record.count_teacher_registrations =\
                len(record.employee_registration_ids)

    @api.multi
    def _compute_count_teacher_pickings_moves(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        for event in self:
            partners = event.mapped('employee_registration_ids.partner_id')
            cond = [('partner_id', 'in', partners.ids)]
            pickings = picking_obj.search(cond)
            event.count_pickings = len(pickings)
            cond = [('picking_id.partner_id', 'in', partners.ids)]
            moves = move_obj.search(cond)
            event.count_moves = len(moves)

    @api.multi
    def _compute_count_presences(self):
        for event in self:
            event.count_presences = len(event.mapped('track_ids.presences'))

    @api.multi
    @api.depends('seats_max', 'registration_ids', 'registration_ids.state',
                 'registration_ids.nb_register')
    def _compute_seats(self):
        super(EventEvent, self)._compute_seats()
        for event in self:
            event.seats_unconfirmed = len(
                event.no_employee_registration_ids.filtered(
                    lambda x: x.state == 'draft'))
            event.seats_reserved = len(
                event.no_employee_registration_ids.filtered(
                    lambda x: x.state in ('open', 'done')))
            event.seats_canceled = len(
                event.no_employee_registration_ids.filtered(
                    lambda x: x.state == 'cancel'))
            event.seats_available = (event.seats_unconfirmed +
                                     event.seats_reserved)

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
    def show_all_registrations(self):
        self.ensure_one()
        return {'name': _('Teacher assistants'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form,calendar,graph',
                'view_type': 'form',
                'res_model': 'event.registration',
                'domain': [('id', 'in', self.registration_ids.ids)]}

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
    def show_presences(self):
        self.ensure_one()
        context = self.env.context.copy()
        context.update({'search_default_students_filter': 1})
        if context.get('group_by', False):
            context.pop('group_by')
        return {'name': _('Event presences'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'event.track.presence',
                'context': context,
                'domain': [('id', 'in',
                            self.mapped('track_ids.presences').ids)]}

    @api.multi
    def show_teacher_pickings(self):
        partners = self.mapped('employee_registration_ids.partner_id')
        return {'name': _('Teachers pickings'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form,calendar',
                'view_type': 'form',
                'res_model': 'stock.picking',
                'domain': [('partner_id', 'in', partners.ids)]}

    @api.multi
    def show_teacher_moves(self):
        partners = self.mapped('employee_registration_ids.partner_id')
        return {'name': _('Teachers moves'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'stock.move',
                'domain': [('picking_id.partner_id', 'in', partners.ids)]}

    def _delete_canceled_presences_registrations(self):
        for event in self:
            presences = event.mapped('track_ids.presences').filtered(
                lambda x: x.state == 'canceled')
            presences.unlink()
            registrations = event.registration_ids.filtered(
                lambda x: x.state == 'cancel')
            for registration in registrations:
                presences = event.mapped('track_ids.presences').filtered(
                    lambda x: x.state != 'canceled' and
                    x.partner.id == registration.partner_id.id)
                if not presences:
                    registration.analytic_account.unlink()
                    registration.write({'state': 'draft'})
                    registration.unlink()


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.depends('event_id', 'event_id.sale_order',
                 'event_id.sale_order.project_id',
                 'event_id.sale_order.project_id.recurring_invoices',
                 'employee', 'analytic_account')
    def _calculate_required_account(self):
        for reg in self:
            reg.required_account = True
            if (reg.employee or reg.analytic_account or
                    reg.event_id.sale_order.project_id.recurring_invoices):
                reg.required_account = False

    required_account = fields.Boolean(
        string='Required account', compute='_calculate_required_account',
        store=True)
    analytic_account = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic account')
    employee = fields.Many2one(
        comodel_name='hr.employee', string='Employee',
        related='partner_id.employee_id', store=True)
    parent_num_bank_accounts = fields.Integer(
        string='# bank accounts', store=True,
        related='partner_id.parent_num_bank_accounts')
    parent_num_valid_mandates = fields.Integer(
        string='# valid mandates', store=True,
        related='partner_id.parent_num_valid_mandates')
    submitted_evaluation = fields.Selection(
        [('yes', _('Yes')),
         ('no', 'No')], string='Submitted evaluation', default='no')
    submitted_evaluation_error = fields.Char(
        string='Submitted evaluation error')

    @api.onchange('partner_id')
    def _onchange_partner(self):
        super(EventRegistration, self)._onchange_partner()
        self.employee = self.partner_id.employee_id

    def _prepare_wizard_registration_open_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_registration_open_vals()
        wiz_vals.update({'create_account': self.required_account})
        return wiz_vals

    @api.multi
    def button_reg_cancel(self):
        self.mapped('analytic_account').set_cancel()
        super(EventRegistration, self).button_reg_cancel()

    def _send_email_to_registrations_with_evaluation(self, body):
        attachment_obj = self.env['ir.attachment']
        template = self.env.ref(
            'event_registration_analytic.email_template_event_registration_'
            'evaluation', False)
        if not template:
            raise exceptions.Warning(
                _("Email template not found to send evaluations to event"
                  " registration"))
        for registration in self:
            vals = {'submitted_evaluation': 'no'}
            cond = [('res_model', '=', 'event.registration'),
                    ('res_id', '=', registration.id)]
            attachments = attachment_obj.search(cond)
            if len(attachments) == 0:
                vals['submitted_evaluation_error'] = _('Attachment not found')
            elif len(attachments) > 1:
                vals['submitted_evaluation_error'] = _('Found more than one '
                                                       'attachment')
            elif not registration.partner_id.parent_id:
                vals['submitted_evaluation_error'] = _('Student without '
                                                       'parent')
            elif not registration.partner_id.parent_id.email:
                vals['submitted_evaluation_error'] = _('Parent without email')
            else:
                wizard = self.env['mail.compose.message'].with_context(
                    default_composition_mode='mass_mail',
                    default_template_id=template.id,
                    default_use_template=True,
                    default_attachment_ids=[(6, 0, attachments.ids)],
                    active_id=registration.id,
                    active_ids=registration.ids,
                    active_model='event.registration',
                    default_model='event.registration',
                    default_res_id=registration.id,
                    force_send=True
                ).create({'body': body})
                wizard.send_mail()
                vals = {'submitted_evaluation': 'yes',
                        'submitted_evaluation_error': ''}
            registration.write(vals)


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
    def _compute_real_duration(self):
        for track in self:
            track.real_duration = (max(track.mapped('presences.real_duration'))
                                   if track.presences else 0)

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
