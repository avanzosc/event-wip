# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, _


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def button_validate_holiday(self):
        self.ensure_one()
        for holiday in self:
            if (holiday.employee_id.address_home_id and
                    holiday.type == 'remove'):
                result = self._find_employee_calendar(holiday, True)
                if result:
                    return result
                holiday.signal_workflow('validate')
                holiday._update_presences_validate_holiday()
                self._update_partner_calendar_day(
                    holiday, absence_type=holiday.holiday_status_id.id)
            else:
                holiday.signal_workflow('validate')

    @api.multi
    def button_refuse_holiday(self):
        self.ensure_one()
        for holiday in self:
            if (holiday.state == 'validate' and holiday.type == 'remove' and
                    holiday.employee_id.address_home_id):
                result = self._find_employee_calendar(holiday, False)
                if result:
                    return result
                holiday._update_presences_refuse_holiday()
                self._update_partner_calendar_day(holiday)
            self.signal_workflow('refuse')

    def _find_employee_calendar(self, holiday, validate_ausence):
        wiz_obj = self.env['wiz.calculate.employee.calendar']
        partner_calendar_obj = self.env['res.partner.calendar']
        event_obj = self.env['event.event']
        employee_with_calendar = True
        from_year = int(event_obj._convert_date_to_local_format_with_hour(
            holiday.date_from).strftime('%Y'))
        to_year = int(event_obj._convert_date_to_local_format_with_hour(
            holiday.date_to).strftime('%Y'))
        while from_year <= to_year:
            cond = [('partner', '=', holiday.employee_id.address_home_id.id),
                    ('year', '=', from_year)]
            calendar = partner_calendar_obj.search(cond)
            if not calendar:
                employee_with_calendar = False
                from_year = to_year
            from_year += 1
        if employee_with_calendar:
            return {}
        wiz = wiz_obj.create({'validate_ausence': validate_ausence,
                              'ausence': holiday.id})
        context = self.env.context.copy()
        context['active_id'] = holiday.id
        context['active_ids'] = [holiday.id]
        context['active_model'] = 'hr.holidays'
        return {'name': _('There is no calendar for the employee, we are going'
                          ' to create'),
                'type': 'ir.actions.act_window',
                'res_model': 'wiz.calculate.employee.calendar',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': wiz.id,
                'target': 'new',
                'context': context}

    def _update_partner_calendar_day(self, holiday, absence_type=False):
        calendar_day_obj = self.env['res.partner.calendar.day']
        event_obj = self.env['event.event']
        date_from = event_obj._convert_date_to_local_format_with_hour(
            holiday.date_from).strftime('%Y-%m-%d')
        date_to = event_obj._convert_date_to_local_format_with_hour(
            holiday.date_to).strftime('%Y-%m-%d')
        cond = [('partner', '=', holiday.employee_id.address_home_id.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to)]
        days = calendar_day_obj.search(cond)
        if absence_type:
            days.write({'absence': True,
                        'absence_type': absence_type})
            return True
        self._update_calendar_days_from_presences(holiday, days)
        return True

    def _update_calendar_days_from_presences(self, holiday, days):
        days.write({'absence': False,
                    'absence_type': False})
        presences = self._catch_employee_presences(holiday)
        for day in days:
            if day.absence_type_from_employee_contract:
                absence_type = day.absence_type_from_employee_contract
                day.write({'festive': True,
                           'absence_type': absence_type.id})
            else:
                for presence in presences:
                    session_date = presence.session_date_without_hour
                    if (session_date == day.date and
                            presence.session.absence_type):
                        day.write({'festive': True,
                                   'absence_type':
                                   presence.session.absence_type.id})
