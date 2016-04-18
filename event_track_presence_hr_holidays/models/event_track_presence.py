# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    hr_holiday = fields.Many2one(
        'hr.holidays', string='Holiday/Absence')
    hr_holiday_absence_type = fields.Many2one(
        'hr.holidays.status', string='Holiday/Absence absence type',
        related='hr_holiday.holiday_status_id', store=True)
