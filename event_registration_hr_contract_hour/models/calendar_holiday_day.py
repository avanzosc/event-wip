# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class CalendarHolidayDay(models.Model):
    _inherit = 'calendar.holiday.day'

    type_hour = fields.Many2one(
        'hr.type.hour', string='Type hour')
