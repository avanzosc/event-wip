# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _
from .._common import _convert_to_local_date, _convert_time_to_float
from dateutil.relativedelta import relativedelta

str2datetime = fields.Datetime.from_string
str2date = fields.Date.from_string
datetime2str = fields.Datetime.to_string
date2str = fields.Date.to_string


class EventEvent(models.Model):
    _inherit = 'event.event'

    claim_ids = fields.One2many(
        comodel_name='crm.claim', inverse_name='event_id', string='Claims')
    claim_count = fields.Integer(
        string='# Claims', compute='_compute_claim_count')

    @api.depends('claim_ids')
    def _compute_claim_count(self):
        for event in self:
            event.claim_count = len(event.claim_ids)

    @api.onchange('date_begin')
    def onchange_date_begin(self):
        self.ensure_one()
        res = {}
        if self.date_begin:
            tracks = self.track_ids.filtered(
                lambda x: x.date and x.date < self.date_begin)
            if tracks:
                track = min(tracks, key=lambda x: x.date)
                res = {'warning': {
                       'title': _('Error in date begin'),
                       'message':
                       (_('Session %s with lower date') % track.name)}}
                self.date_begin = track.date
        return res

    @api.onchange('date_end')
    def onchange_date_end(self):
        self.ensure_one()
        res = {}
        if self.date_end:
            tracks = self.track_ids.filtered(
                lambda x: x.date and x.date > self.date_end)
            if tracks:
                track = max(tracks, key=lambda x: x.date)
                res = {'warning': {
                       'title': _('Error in date end'),
                       'message':
                       (_('Session %s with greater date') % track.name)}}
                self.date_end = track.date
        return res

    @api.multi
    def button_mass_mailing_to_organizer(self):
        ir_model_data = self.env['ir.model.data']
        self._validate_organizer_email()
        template_id = self.env.ref(
            'event_track_assistant.email_to_event_organizer', False)
        if not template_id:
            raise exceptions.Warning(
                _("Email template not found for event organizer"))
        compose_form_id = (ir_model_data.get_object_reference(
            'mail', 'email_compose_message_wizard_form') and
            ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1] or False)
        ctx = {
            'default_model': 'event.event',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'mass_mail'}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx}

    def _validate_organizer_email(self):
        if self.organizer_id.notify_email == 'none':
            raise exceptions.Warning(
                _("Organizer %s does not want to be sent email, if you want to"
                  " send email, modify this information in the tab of the "
                  "organizer.") % self.organizer_id.name)
        if (self.organizer_id.notify_email == 'always' and not
                self.organizer_id.email):
            raise exceptions.Warning(
                _("Organizer %s without email.") % self.organizer_id.name)

    @api.multi
    def button_mass_mailing_to_registrations(self):
        wiz_obj = self.env['wiz.send.email.to.registrations']
        self._validate_registrations_email()
        wiz = wiz_obj.with_context(
            {'active_id': self.id,
             'active_ids': self.ids,
             'active_model': 'event.event'}).create({})
        context = self.env.context.copy()
        context.update({
            'active_id': self.id,
            'active_ids': self.ids,
            'active_model': 'event.event',
        })
        return {
            'name': _('Send email to event registrations'),
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.send.email.to.registrations',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': wiz.id,
            'target': 'new',
            'context': context,
        }

    def _validate_registrations_email(self):
        for event in self:
            registrations = event.mapped('registration_ids').filtered(
                lambda x: x.partner_id.notify_email == 'always' and not
                x.partner_id.email)
            for registration in registrations:
                raise exceptions.Warning(_("Partner %s without email.") %
                                         registration.partner_id.name)

    def _send_email_to_registrations(self, body):
        template = self.env.ref(
            'event_registration_mass_mailing.email_template_event_'
            'registration', False)
        if not template:
            raise exceptions.Warning(
                _("Email template not found for event registration"))
        for event in self:
            for registration in event.registration_ids:
                wizard = self.env['mail.compose.message'].with_context(
                    default_composition_mode='mass_mail',
                    default_template_id=template.id,
                    default_use_template=True,
                    active_id=registration.id,
                    active_ids=registration.ids,
                    active_model='event.registration',
                    default_model='event.registration',
                    default_res_id=registration.id,
                ).create({'body': body})
                wizard.send_mail()


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.depends('date', 'duration')
    def _compute_estimated_date_end(self):
        for track in self.filtered(lambda t: t.date and t.duration):
            new_date = str2datetime(track.date) +\
                relativedelta(hours=track.duration)
            track.estimated_date_end = new_date

    @api.depends('event_id', 'event_id.registration_ids', 'session_date')
    def _compute_allowed_partner_ids(self):
        for track in self.filtered(lambda x: x.session_date):
            registrations = self.env['event.registration']
            for registration in track.mapped(
                'event_id.registration_ids').filtered(
                    lambda x: x.date_start and x.date_end):
                date_start = date2str(_convert_to_local_date(
                    registration.date_start, self.env.user.tz).date())
                date_end = date2str(_convert_to_local_date(
                    registration.date_end, self.env.user.tz).date())
                if (track.session_date >= date_start and
                        track.session_date <= date_end):
                    registrations += registration
            partners = registrations.mapped('partner_id')
            track.allowed_partner_ids = [(6, 0, partners.ids)]

    @api.depends('presences', 'presences.real_duration')
    def _compute_real_duration(self):
        for track in self:
            track.real_duration = sum(track.mapped('presences.real_duration'))

    @api.depends('date', 'real_duration')
    def _compute_real_date_end(self):
        for track in self.filtered(lambda t: t.date and t.real_duration):
            new_date = str2datetime(track.date) +\
                relativedelta(hours=track.real_duration)
            track.real_date_end = new_date

    @api.depends('date')
    def _compute_session_date(self):
        for track in self.filtered('date'):
            from_date = _convert_to_local_date(track.date, self.env.user.tz)
            track.session_date = from_date.date()
            track.day = str(from_date.date().weekday())

    @api.depends('estimated_date_end')
    def _compute_session_end_date(self):
        for track in self.filtered('estimated_date_end'):
            from_date = _convert_to_local_date(
                track.estimated_date_end, self.env.user.tz)
            track.session_end_date = from_date.date()

    @api.depends('presences')
    def _compute_num_presences(self):
        for track in self:
            track.lit_presences = _('Presences: ') + str(len(track.presences))

    estimated_date_end = fields.Datetime(
        string='Estimated date end', compute='_compute_estimated_date_end',
        store=True)
    allowed_partner_ids = fields.Many2many(
        comodel_name="res.partner", relation="rel_partner_event_track",
        column1="event_track_id", column2="partner_id", string="Partners",
        copy=False, compute='_compute_allowed_partner_ids', store=True)
    presences = fields.One2many(
        comodel_name='event.track.presence', inverse_name='session',
        string='Presences')
    duration = fields.Float(string='Estimated duration', digits=(12, 4))
    real_duration = fields.Float(
        compute='_compute_real_duration', string='Real duration', store=True)
    real_date_end = fields.Datetime(
        string='Real date end', compute='_compute_real_date_end',
        store=True)
    session_date = fields.Date(
        string='Session date', compute='_compute_session_date', store=True)
    session_end_date = fields.Date(
        string='Session end date', compute='_compute_session_end_date',
        store=True)
    lit_presences = fields.Char(
        string='Num. presences', compute='_compute_num_presences',
        store=True)
    claim_ids = fields.One2many(
        comodel_name='crm.claim', inverse_name='session_id', string='Claims')
    claim_count = fields.Integer(
        string='# Claims', compute='_compute_claim_count')
    day = fields.Selection(
        selection=[('0', 'Monday'),
                   ('1', 'Tuesday'),
                   ('2', 'Wednesday'),
                   ('3', 'Thursday'),
                   ('4', 'Friday'),
                   ('5', 'Saturday'),
                   ('6', 'Sunday')],
        string='Day of the week', compute='_compute_session_date', store=True)

    @api.depends('claim_ids')
    def _compute_claim_count(self):
        for track in self:
            track.claim_count = len(track.claim_ids)

    @api.constrains('date')
    def _check_session_date(self):
        tz = self.env.user.tz
        date_begin = _convert_to_local_date(self.event_id.date_begin, tz)
        session_date = str2datetime(self.session_date)\
            if self.session_date else False
        if session_date and session_date.date() < date_begin.date():
            raise exceptions.Warning(
                _('Session %s with date lower than the event start date')
                % self.name)
        date_end = _convert_to_local_date(self.event_id.date_end, tz)
        if session_date and session_date.date() > date_end.date():
            raise exceptions.Warning(
                _('Session %s with date greater than the event start date')
                % self.name)


class EventTrackPresence(models.Model):
    _name = 'event.track.presence'
    _description = 'Session assistants'

    @api.depends('session', 'session.allowed_partner_ids')
    def _compute_allowed_partner_ids(self):
        for presence in self:
            presence.allowed_partner_ids = (
                [(6, 0, presence.session.allowed_partner_ids.ids)])
            if self.env['marketing.config.settings']._get_parameter(
               'show.all.customers.in.presences'):
                customers = self.env['res.partner'].search([])
                for customer in customers:
                    presence.allowed_partner_ids = [(4, customer.id)]

    @api.depends('session_date', 'real_duration')
    def _compute_real_date_end(self):
        for presence in self.filtered('real_duration'):
            start_date = str2datetime(presence.session_date)
            end_date = start_date + relativedelta(
                hours=presence.real_duration)
            presence.real_date_end = end_date
            daytime, nighttime = presence._get_nightlight_hours(start_date,
                                                                end_date)
            presence.real_daylight_hours = daytime
            presence.real_nightlight_hours = nighttime

    @api.depends('session_date', 'session_duration')
    def _compute_estimated_daynightlight_hours(self):
        for presence in self.filtered('session_duration'):
            start_date = str2datetime(presence.session_date)
            end_date = start_date + relativedelta(
                hours=presence.session_duration)
            daytime, nighttime = presence._get_nightlight_hours(start_date,
                                                                end_date)
            presence.estimated_daylight_hours = daytime
            presence.estimated_nightlight_hours = nighttime

    name = fields.Char(
        string='Partner', related='partner.name', store=True)
    session = fields.Many2one(
        comodel_name='event.track', string='Session', ondelete='cascade')
    event = fields.Many2one(
        comodel_name='event.event', string='Event', store=True,
        related='session.event_id')
    allowed_partner_ids = fields.Many2many(
        comodel_name='res.partner', compute='_compute_allowed_partner_ids',
        string='Allowed partners')
    session_date = fields.Datetime(
        related='session.date', string='Session date', store=True)
    session_date_without_hour = fields.Date(
        string='Session date without hour', related='session.session_date',
        store=True)
    session_end_date_without_hour = fields.Date(
        string='Session end date without hour',
        related='session.session_end_date', store=True)
    session_duration = fields.Float(
        related='session.duration', string='Duration', store=True)
    partner = fields.Many2one(
        comodel_name='res.partner', string='Partner', required=True)
    real_duration = fields.Float(string='Real duration', default=0.0)
    estimated_date_end = fields.Datetime(
        string='Estimated date end', related='session.estimated_date_end',
        store=True)
    real_date_end = fields.Datetime(
        string='Real date end', compute='_compute_real_date_end', store=True)
    estimated_daylight_hours = fields.Float(
        string='Estimated daylight hours', default=0.0,
        compute='_compute_estimated_daynightlight_hours', store=True)
    estimated_nightlight_hours = fields.Float(
        string='Estimated nightlight hours', default=0.0,
        compute='_compute_estimated_daynightlight_hours', store=True)
    real_daylight_hours = fields.Float(
        string='Real daylight hours', default=0.0,
        compute='_compute_real_date_end', store=True)
    real_nightlight_hours = fields.Float(
        string='Real nightlight hours', default=0.0,
        compute='_compute_real_date_end', store=True)
    notes = fields.Text(string='Notes')
    state = fields.Selection(
        selection=[('pending', 'Pending'), ('completed', 'Completed'),
                   ('absent', 'Absent'), ('canceled', 'Canceled')],
        string="State", default='pending', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', store=True,
        related='session.event_id.company_id')
    session_day = fields.Selection(
        string='Session day of the week', related='session.day', store=True)

    @api.multi
    def button_completed(self):
        presences = self.filtered(lambda x: not x.real_duration)
        for presence in presences:
            presence.real_duration = presence.session_duration
        self.write({'state': 'completed'})

    @api.multi
    def button_canceled(self):
        self.write({'state': 'canceled'})

    @api.multi
    def button_pending(self):
        self.write({'real_duration': 0,
                    'state': 'pending'})

    @api.multi
    def button_absent(self):
        self.write({'real_duration': 0,
                    'state': 'absent'})
        self.count_absences_create_claim()

    def _get_nightlight_hours(self, start_date, end_date):
        company_obj = self.env['res.company']
        company_id = self.event.company_id.id or\
            company_obj._company_default_get('event.track.presence')
        company = company_obj.browse(company_id)
        tz = self.env.user.tz
        daytime = nighttime = 0
        start_date = str2datetime(start_date)\
            if isinstance(start_date, str) else start_date
        end_date = str2datetime(end_date) \
            if isinstance(end_date, str) else end_date
        if start_date >= end_date:
            raise exceptions.ValidationError(
                _('Dates are incorrectly selected.'))
        start_hour = _convert_time_to_float(start_date, tz)
        start_date = _convert_to_local_date(start_date, tz)
        end_hour = _convert_time_to_float(end_date, tz)
        end_date = _convert_to_local_date(end_date, tz)
        daytime_start = company.daytime_start_hour
        nighttime_start = company.nighttime_start_hour
        if start_date.date() == end_date.date():
            if ((start_hour < daytime_start and end_hour < daytime_start) or
                    (start_hour > nighttime_start and
                     end_hour > nighttime_start)):
                nighttime += end_hour - start_hour
            elif ((start_hour >= daytime_start and
                    start_hour <= nighttime_start) and
                    (end_hour >= daytime_start and
                     end_hour <= nighttime_start)):
                daytime += end_hour - start_hour
            elif ((start_hour < daytime_start and
                    (end_hour >= daytime_start and
                     end_hour <= nighttime_start))):
                daytime += end_hour - daytime_start
                nighttime += daytime_start - start_hour
            elif ((start_hour >= daytime_start and
                    start_hour <= nighttime_start) and
                    (end_hour > nighttime_start)):
                daytime += nighttime_start - start_hour
                nighttime += end_hour - nighttime_start
            elif (start_hour < daytime_start and end_hour > nighttime_start):
                nighttime += ((daytime_start - start_hour) +
                              (end_hour - nighttime_start))
                daytime += (nighttime_start - daytime_start)
        else:
            if (start_hour < daytime_start):
                daytime += nighttime_start - daytime_start
                nighttime += 24 - (nighttime_start - daytime_start) -\
                    start_hour
            elif (start_hour >= daytime_start and
                    start_hour <= nighttime_start):
                daytime += nighttime_start - start_hour
                nighttime += 24 - nighttime_start
            elif (start_hour > nighttime_start):
                nighttime += 24 - start_hour
            if (end_hour < daytime_start):
                nighttime += end_hour
            elif (end_hour >= daytime_start and
                    end_hour <= nighttime_start):
                daytime += end_hour - daytime_start
                nighttime += daytime_start
            elif (end_hour > nighttime_start):
                daytime += nighttime_start - daytime_start
                nighttime += end_hour - (nighttime_start - daytime_start)
            alldays = (end_date.date() - start_date.date()).days
            daytime += (alldays - 1) * (nighttime_start - daytime_start)
            nighttime += (alldays - 1) *\
                (24 - (nighttime_start - daytime_start))
        return daytime, nighttime

    def _update_presence_duration(self, hours, state=False, notes=False):
        vals = {'real_duration': hours}
        if state:
            vals['state'] = state
        if notes:
            vals['notes'] = notes
        self.write(vals)

    def count_absences_create_claim(self):
        claim_obj = self.env['crm.claim']
        for presence in self:
            presences = presence.event.mapped(
                'track_ids.presences').filtered(
                lambda x: x.partner == presence.partner and
                x.session_date_without_hour <
                presence.session_date_without_hour)
            if (len(presences) >= 2 and not presences[-2:].filtered(
                    lambda x: x.state != 'absent')):
                name = _(u'Event: {}, session: {}').format(
                    presence.event.name, presence.session.name)
                description = _(u'SESSION DATE: {}, PERSON: {}, with 3 '
                                'consecutive leaves.').format(
                    presence.session.date, presence.partner.name)
                claim_vals = {
                    'name': name,
                    'user_id': presence.event.user_id.id,
                    'partner_id': self.env.user.partner_id.id,
                    'email_from': self.env.user.partner_id.email,
                    'description': description,
                    'event_id': presence.event.id,
                    'session_id': presence.session.id,
                    'ref': '{},{}'.format(presence._name, presence.id),
                    'categ_id': self.env.ref('event_track_assistant.crm_case_'
                                             'categ_possible_low').id}
                claim_obj.create(claim_vals)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    notes = fields.Text(string='Notes')
    removal_date = fields.Date(string='Removal date')
    date_start = fields.Datetime(string='Date start')
    date_end = fields.Datetime(string='Date end')
    state = fields.Selection(
        selection=[('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
                   ('open', 'Confirmed'), ('done', 'Finalized')])

    @api.onchange('partner_id')
    def _onchange_partner(self):
        warning = {}
        title = False
        if (self.partner_id and
                self.partner_id.event_registration_warn != 'no-message'):
            title = _("Warning for %s") % self.partner_id.name
            warning = {'title': title,
                       'message': self.partner_id.event_registration_warn_msg}
            if self.partner_id.event_registration_warn == 'block':
                self.partner_id = False
                return {'warning': warning}
        super(EventRegistration, self)._onchange_partner()
        self.date_start = self.event_id.date_begin if self.partner_id else\
            False
        self.date_end = self.event_id.date_end if self.partner_id else False
        if warning:
            return {'warning': warning}

    @api.multi
    @api.onchange('date_start')
    def _onchange_date_start(self):
        self.ensure_one()
        res = {}
        if self.date_start and self.date_start < self.event_id.date_begin:
            self.date_start = self.event_id.date_begin
            return {'warning': {
                    'title': _('Error in date start'),
                    'message':
                    (_('Date start of registration less than date begin of'
                       ' event'))}}
        if (self.date_start and self.date_end and
                self.date_start > self.date_end):
            self.date_start = self.event_id.date_begin
            return {'warning': {
                    'title': _('Error in date start'),
                    'message':
                    (_('Date start of registration greater than date end of'
                       ' event'))}}
        return res

    @api.multi
    @api.onchange('date_end')
    def _onchange_date_end(self):
        self.ensure_one()
        res = {}
        if self.date_end and self.date_end > self.event_id.date_end:
            self.date_end = self.event_id.date_end
            return {'warning': {
                    'title': _('Error in date end'),
                    'message':
                    (_('Date end of registration greater than date end of'
                       ' event'))}}
        if (self.date_end and self.date_start and
                self.date_end < self.date_start):
            self.date_end = self.event_id.date_end
            return {'warning': {
                    'title': _('Error in date end'),
                    'message':
                    (_('Date end of registration less than date start of'
                       ' event'))}}
        return res

    @api.multi
    def button_registration_open(self):
        self.ensure_one()
        wiz_obj = self.env['wiz.event.append.assistant']
        if self.date_start and self.date_end:
            registrations = self.event_id.registration_ids.filtered(
                lambda x: x.id != self.id and x.partner_id and x.date_start and
                x.date_end and x.state in ('done', 'open') and
                x.partner_id.id == self.partner_id.id and
                ((self.date_end >= x.date_start and
                  self.date_end <= x.date_end) or
                 (self.date_start <= x.date_end and self.date_start >=
                  x.date_start)))
            if registrations:
                raise exceptions.Warning(
                    _('You can not confirm this registration, because their'
                      ' dates overlap with another record of the same'
                      ' employee'))
        wiz = wiz_obj.with_context(
            {'active_id': self.event_id.id,
             'active_ids': self.event_id.ids,
             'active_model': 'event.event'}).create(
            self._prepare_wizard_registration_open_vals())
        context = self.env.context.copy()
        context.update({
            'active_id': self.event_id.id,
            'active_ids': self.event_id.ids,
            'active_model': 'event.event',
        })
        return {'name': _('Add Person To Session'),
                'type': 'ir.actions.act_window',
                'res_model': 'wiz.event.append.assistant',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': wiz.id,
                'target': 'new',
                'context': context}

    def _prepare_wizard_registration_open_vals(self):
        tz = self.env.user.tz
        min_from_date = _convert_to_local_date(self.event_id.date_begin, tz)
        max_to_date = _convert_to_local_date(self.event_id.date_end, tz)
        from_date = _convert_to_local_date(self.date_start, tz)\
            if self.date_start else min_from_date
        to_date = _convert_to_local_date(self.date_end, tz)\
            if self.date_end else max_to_date
        wiz_vals = {
            'registration': self.id,
            'partner': self.partner_id.id,
            'min_event': self.event_id.id,
            'max_event': self.event_id.id,
            'from_date': from_date.date(),
            'min_from_date': min_from_date,
            'to_date': to_date.date(),
            'max_to_date': max_to_date,
        }
        return wiz_vals

    @api.multi
    def button_reg_cancel(self):
        if any(self.filtered(lambda r: not r.notes)):
            raise exceptions.Warning(
                _('Notes are mandatory to cancel a registration.'))
        self.filtered(lambda r: not r.removal_date).write({
            'removal_date': fields.Date.context_today(self),
        })
        super(EventRegistration, self).button_reg_cancel()
        self.message_post(body=_('Event Registration canceled.'))

    @api.multi
    def new_button_reg_cancel(self):
        self.ensure_one()
        wiz_obj = self.env['wiz.event.delete.assistant']
        wiz = wiz_obj.with_context(active_ids=self.event_id.id).create(
            self._prepare_wizard_reg_cancel_vals())
        context = self.env.context.copy()
        context.update({
            'active_id': self.event_id.id,
            'active_ids': self.event_id.ids,
            'active_model': 'event.event',
        })
        return {
            'name': _('Delete Person From Event-Session'),
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.event.delete.assistant',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': wiz.id,
            'target': 'new',
            'context': context,
        }

    def _prepare_wizard_reg_cancel_vals(self):
        tz = self.env.user.tz
        min_from_date = _convert_to_local_date(self.event_id.date_begin, tz=tz)
        max_to_date = _convert_to_local_date(self.event_id.date_end, tz=tz)
        from_date = _convert_to_local_date(self.date_start, tz=tz)\
            if self.date_start else min_from_date
        to_date = _convert_to_local_date(self.date_end, tz=tz)\
            if self.date_end else max_to_date
        today = fields.Date.context_today(self)
        wiz_vals = {
            'registration': self.id,
            'partner': self.partner_id.id,
            'from_date': from_date.date() if date2str(from_date) >= today
            else today,
            'min_from_date': min_from_date,
            'to_date': to_date.date(),
            'max_to_date': max_to_date,
        }
        return wiz_vals

    @api.multi
    def unlink(self):
        if any(self.filtered(lambda r: r.state != 'draft')):
            raise exceptions.Warning(
                _('You can only delete registration in draft status.'))
        return super(EventRegistration, self).unlink()
