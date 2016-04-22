# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_event_data(self, sale, line, name, project):
        event_obj = self.env['event.event']
        res = super(SaleOrder, self)._prepare_event_data(sale, line, name,
                                                         project)
        if self.project_id.date_start:
            if line.project_by_task:
                time = line.start_hour
            else:
                time = self.project_id.start_time or 0
            utc_dt = event_obj._put_utc_format_date(self.project_id.date_start,
                                                    time)
            res['date_begin'] = utc_dt
        if self.project_id.date:
            time = self.project_id.end_time or 0
            utc_dt = event_obj._put_utc_format_date(self.project_id.date, time)
            res['date_end'] = utc_dt
        if sale.project_id.type_hour:
            res['type_hour'] = sale.project_id.type_hour.id
        return res

    def _prepare_session_data_from_sale_line(
            self, event, num_session, line, date):
        vals = super(SaleOrder, self)._prepare_session_data_from_sale_line(
            event, num_session, line, date)
        time = self.project_id.start_time or 0
        if line.project_by_task:
            vals['date'] = event._put_utc_format_date(date, line.start_hour)
        else:
            vals['date'] = event._put_utc_format_date(date, time)
        if line.order_id.project_id.type_hour:
            vals['type_hour'] = line.order_id.project_id.type_hour.id
        return vals
