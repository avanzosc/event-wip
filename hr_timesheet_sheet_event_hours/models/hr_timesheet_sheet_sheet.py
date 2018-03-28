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
            from_date = '{} 00:00:00'.format(sheet.date_from)
            to_date = '{} 23:59:59'.format(sheet.date_to)
            cond = [('event_id', '!=', False),
                    ('user_id', '=', sheet.user_id.id),
                    ('date', '>=', from_date),
                    ('date', '<=', to_date)]
            works = self.env['project.task.work'].search(cond)
            sheet.total_hours_worked = sum(works.mapped('hours'))
            cond = [('date', '>=', sheet.date_from),
                    ('date', '<=', sheet.date_to),
                    ('partner', '=', sheet.employee_id.address_home_id.id),
                    ('festive', '=', True)]
            festives = self.env['res.partner.calendar.day'].search(cond)
            sheet.festive_hours_worked = sum(
                works.filtered(lambda x: x.date[0:10] in
                               festives.mapped('date')).mapped('hours'))
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
