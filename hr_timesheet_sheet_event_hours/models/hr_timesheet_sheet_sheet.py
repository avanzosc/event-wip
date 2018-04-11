# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class HrTimesheetSheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    def _compute_month_hours(self):
        for sheet in self:
            cond = [('partner', '=', sheet.employee_id.address_home_id.id),
                    ('session_date_without_hour', '>=', sheet.date_from),
                    ('session_date_without_hour', '<=', sheet.date_to),
                    ('replaced_by', '=', False),
                    ('state', 'in', ('pending', 'completed'))]
            presences = self.env['event.track.presence'].search(cond)
            sheet.month_hours = sum(presences.mapped('session_duration'))
            cond = [('partner', '=', sheet.employee_id.address_home_id.id),
                    ('date', '>=', sheet.date_from),
                    ('date', '<=', sheet.date_to),
                    ('festive', '=', True)]
            festive_dates = self.env['res.partner.calendar.day'].search(
                cond).mapped('date')
            sheet.timesheet_ids.write({'festive': False})
            times = sheet.timesheet_ids.filtered(
                lambda x: x.line_id and x.line_id.date in festive_dates)
            times.write({'festive': True})
            sheet.total_hours_worked = sum(
                sheet.mapped('timesheet_ids.line_id.unit_amount'))
            sheet.festive_hours_worked = sum(times.mapped('unit_amount'))
            sheet.working_hours_worked = (
                sheet.total_hours_worked - sheet.festive_hours_worked)

    month_hours = fields.Float(
        string='Month hours', compute='_compute_month_hours')
    festive_hours_worked = fields.Float(
        string='Festive hours worked', compute='_compute_month_hours')
    working_hours_worked = fields.Float(
        string='Working hours worked', compute='_compute_month_hours')
    total_hours_worked = fields.Float(
        string='Total hours worked', compute='_compute_month_hours')
