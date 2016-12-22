# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.multi
    def _put_festives_in_sesions_from_sale_contract(self, calendars):
        for track in self.mapped('track_ids'):
            track_date = fields.Date.from_string(track.session_date)
            for day in calendars.mapped('lines'):
                day_date = fields.Date.from_string(day.date)
                if track_date.month == day_date.month and\
                        track_date.day == day_date.day:
                    track.write({
                        'absence_type': day.absence_type.id,
                        'sale_contract_absence_type': day.absence_type.id})


class EventTrack(models.Model):
    _inherit = 'event.track'

    absence_type = fields.Many2one(
        'hr.holidays.status', string='Absence type')
    sale_contract_absence_type = fields.Many2one(
        'hr.holidays.status', string='Absence type from sale contract')


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    @api.depends('session_date_without_hour')
    def _calculate_partner_calendar_day(self):
        day_obj = self.env['res.partner.calendar.day']
        for presence in self:
            presence.partner_calendar_day = False
            if presence.session_date_without_hour:
                cond = [('partner', '=', presence.partner.id),
                        ('date', '=', presence.session_date_without_hour)]
                day = day_obj.search(cond, limit=1)
                if day:
                    presence.partner_calendar_day = day.id

    partner_calendar_day = fields.Many2one(
        'res.partner.calendar.day', string='Employee calendar day',
        compute='_calculate_partner_calendar_day', store=True)
    absence_type = fields.Many2one(
        'hr.holidays.status', string='Absence type')
    sale_contract_absence_type = fields.Many2one(
        'hr.holidays.status', string='Absence type from sale contract',
        related='session.sale_contract_absence_type', store=True)
    calendar_holiday_absence_type = fields.Many2one(
        'hr.holidays.status', string='Absence type from employee contract',
        related='partner_calendar_day.absence_type_from_employee_contract',
        store=True)

    @api.model
    def create(self, vals):
        presence = super(EventTrackPresence, self).create(vals)
        day = presence.partner_calendar_day
        if (not presence.absence_type and
                day.absence_type_from_employee_contract):
            presence.absence_type = day.absence_type_from_employee_contract.id
        return presence

    @api.multi
    def button_mark_presence_as_worked(self):
        self.ensure_one()
        self.state = 'completed'
        if not self.absence_type:
            self.real_duration = self.session_duration
