# -*- coding: utf-8 -*-
# © 2017 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from openerp.addons.event_track_assistant._common import _convert_to_utc_date


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    date_from = fields.Date(string='Date from')
    attendance_historical_ids = fields.One2many(
        comodel_name='resource.calendar.attendance.historical',
        inverse_name='calendar_id', string='History of schedules',
        copy=False)

    def _calc_date_and_duration(self, date):
        lines = self.mapped('attendance_ids').filtered(
            lambda x: x.dayofweek == str(date.date().weekday()))
        if not lines:
            return False, False
        min_h = min(lines, key=lambda x: x.hour_from)
        new_date = _convert_to_utc_date(
            date, min_h.hour_from, tz=self.env.user.tz)
        duration = sum(x['hour_to'] - x['hour_from'] for x in lines)
        return new_date, duration


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    @api.multi
    def write(self, values):
        historical_obj = self.env['resource.calendar.attendance.historical']
        if (values.get('dayofweek', False) or values.get('date_from', False) or
            values.get('hour_from', False) or
                values.get('hour_to', False)):
            for line in self:
                vals = {'name': line.name,
                        'dayofweek': line.dayofweek,
                        'date_from': line.date_from,
                        'hour_from': line.hour_from,
                        'hour_to': line.hour_to,
                        'calendar_id': line.calendar_id.id}
                historical_obj.create(vals)
        return super(ResourceCalendarAttendance, self).write(values)


class ResourceCalendarAttendanceHistorical(models.Model):
    _name = 'resource.calendar.attendance.historical'
    _description = 'History of schedules'
    _order = 'dayofweek, id'

    name = fields.Char(string='Name', required=True)
    dayofweek = fields.Selection(
        selection=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
                   ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'),
                   ('6', 'Sunday')], string='day of week')
    date_from = fields.Date(string='Starting date')
    hour_from = fields.Float(string='Work from')
    hour_to = fields.Float(string='Work to')
    calendar_id = fields.Many2one(
        comodel_name='resource.calendar', string="Resource's Calendar",
        ondelete='cascade')
