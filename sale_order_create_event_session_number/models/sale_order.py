# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, fields, exceptions, _
from openerp.addons.event_track_assistant._common import _convert_to_utc_date
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for sale in self.filtered('project_id'):
            sale_lines = sale.order_line.filtered(
                lambda x: x.recurring_service)
            lines = sale_lines.filtered(
                lambda x: not x.end_date and not x.session_number)
            if lines:
                bad_lines = ''
                for line in lines:
                    bad_lines += '{}, '.format(line.name)
                    raise exceptions.Warning(
                        _("You must enter the number of sessions, or the end"
                          " date, for lines: '%s'") % (bad_lines))
            lines = sale_lines.filtered(lambda x: x.session_number > 0)
            self._generate_lines_end_date(lines)
        return super(SaleOrder, self).action_button_confirm()

    def _generate_lines_end_date(self, lines):
        task_obj = self.env['project.task']
        tz = self.env.user.tz
        for l in lines:
            fec_ini = (
                l.project_by_task == 'yes' and
                _convert_to_utc_date(l.start_date, l.start_hour, tz=tz) or
                fields.Datetime.from_string(self.project_id.date_start))
            fec_ini = fec_ini.replace(day=1)
            num_week = fec_ini.weekday() == 0 and 0 or 1
            month = fec_ini.month
            session_number = 0
            end_date = ''
            while session_number <= l.session_number:
                if month != fec_ini.month:
                    month = fec_ini.month
                    num_week = fec_ini.weekday() == 0 and 0 or 1
                if fec_ini.weekday() == 0:
                    num_week += 1
                l_fec_ini = (
                    l.project_by_task == 'yes' and _convert_to_utc_date(
                        l.start_date, l.start_hour, tz=tz) or
                    fields.Datetime.from_string(self.project_id.date_start))
                if fec_ini.date() >= l_fec_ini.date():
                    valid = task_obj._validate_event_session_month(
                        l, fec_ini)
                    if valid:
                        valid = task_obj._validate_event_session_week(
                            l, num_week)
                    if valid:
                        valid = task_obj._validate_event_session_day(
                            l, fec_ini)
                    if valid:
                        session_number += 1
                        end_date = fec_ini
                        if session_number == l.session_number:
                            l.end_date = end_date
                fec_ini = fec_ini + relativedelta(days=+1)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    session_number = fields.Integer(
        string='Sessions number to generate', default=0)
