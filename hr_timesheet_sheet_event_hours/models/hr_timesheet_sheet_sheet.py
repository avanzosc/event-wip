# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class HrTimesheetSheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    def _compute_month_hours(self):
        for sheet in self:
            cond = [('partner', '=', sheet.employee_id.address_home_id.id),
                    ('session_date_without_hour', '>=', sheet.date_from),
                    ('session_date_without_hour', '<=', sheet.date_to)]
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
            sheet.difference = sheet.total_hours_worked - sheet.month_hours

    def _compute_contract_hours(self):
        contract_obj = self.env['hr.contract']
        for sheet in self.filtered(lambda x: x.employee_id and x.date_from):
            cond = [('employee_id', '=', sheet.employee_id.id),
                    ('date_start', '<=', sheet.date_from)]
            contracts = contract_obj.search(cond)
            if contracts:
                contract = max(contracts, key=lambda x: x.date_start)
                if contract.history_ids:
                    history = max(contract.history_ids, key=lambda x: x.date)
                    sheet.write({'contract_hours': history.hours,
                                 'percentage': history.percentage})
                    sheet.contract_hours = history.hours

    month_hours = fields.Float(
        string='Estimated hours', compute='_compute_month_hours')
    festive_hours_worked = fields.Float(
        string='Festive hours worked', compute='_compute_month_hours')
    working_hours_worked = fields.Float(
        string='Working hours worked', compute='_compute_month_hours')
    total_hours_worked = fields.Float(
        string='Total hours worked', compute='_compute_month_hours')
    difference = fields.Float(
        string='Difference', compute='_compute_month_hours')
    contract_hours = fields.Float(
        string='Contract hours', compute='_compute_contract_hours')
    percentage = fields.Float(
        string='Percentage', compute='_compute_contract_hours')
    weekly_hours_ids = fields.One2many(
        comodel_name='hr_timesheet_sheet.sheet.weekly.hour',
        inverse_name='hr_timesheet_sheet_id', string='Weekly hours',)

    @api.multi
    def button_recalculate_weekly_hours(self):
        for sheet in self:
            sheet.weekly_hours_ids.unlink()
            list = {}
            for line in sheet.timesheet_ids:
                date = fields.Date.from_string(line.date)
                week = date.strftime("%W")
                if week not in list:
                    list[week] = line.unit_amount
                else:
                    amount = list.get(week)
                    list[week] = amount + line.unit_amount
            months = list.keys()
            vals = []
            for month in months:
                vals.append((0, 0, {'name': month, 'hours': list.get(month)}))
            if vals:
                sheet.write({'weekly_hours_ids': vals})


class HrTimesheetSheetSheetWeeklyHour(models.Model):
    _name = 'hr_timesheet_sheet.sheet.weekly.hour'
    _description = 'Hours worked per week'
    _order = 'name'

    hr_timesheet_sheet_id = fields.Many2one(
        comodel_name='hr_timesheet_sheet.sheet', string='Sheet')
    name = fields.Char(string='Week')
    hours = fields.Float(string='Hours')
