# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models
from openerp.addons.event_track_assistant._common import _convert_to_utc_date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_event_data(self, sale, line, name, project):
        res = super(SaleOrder, self)._prepare_event_data(sale, line, name,
                                                         project)
        if not line or (line and line.project_by_task == 'no'):
            utc_dt = _convert_to_utc_date(
                self.project_id.date_start, time=self.project_id.start_time,
                tz=self.env.user.tz)
            res['date_begin'] = utc_dt
        if not line or (line and line.project_by_task == 'no'):
            utc_dt = _convert_to_utc_date(
                self.project_id.date, time=self.project_id.end_time,
                tz=self.env.user.tz)
            res['date_end'] = utc_dt
        if sale.project_id.type_hour:
            res['type_hour'] = sale.project_id.type_hour.id
        return res

    def _prepare_session_data_from_sale_line(
            self, event, num_session, line, date):
        vals = super(SaleOrder, self)._prepare_session_data_from_sale_line(
            event, num_session, line, date)
        if line.project_by_task == 'no':
            new_date = False
            if self.project_id.working_hours:
                working = self.project_id.working_hours
                new_date, duration = working._calc_date_and_duration(date)
            vals['date'] = new_date or _convert_to_utc_date(
                date, time=self.project_id.start_time,
                tz=self.env.user.tz)
        if line.order_id.project_id.type_hour:
            vals['type_hour'] = line.order_id.project_id.type_hour.id
        return vals
