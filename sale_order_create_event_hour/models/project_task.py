# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models
from openerp.addons.event_track_assistant._common import _convert_to_utc_date


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _create_new_account_project_by_task(self, task, parent_account, code):
        account = super(ProjectTask, self)._create_new_account_project_by_task(
            task, parent_account, code)
        if parent_account.type_hour:
            account.type_hour = parent_account.type_hour.id
        return account

    def _account_info_for_create_task_service_project(self, vals, procurement):
        event_obj = self.env['event.event']
        tz = self.env.user.tz
        vals = super(
            ProjectTask, self)._account_info_for_create_task_service_project(
            vals, procurement)
        if (procurement.sale_line_id.order_id.project_id.date_start and
                procurement.sale_line_id.order_id.project_id.start_time):
            date_start = event_obj._convert_date_to_local_format(
                procurement.sale_line_id.order_id.project_id.date_start).date()
            time = procurement.sale_line_id.order_id.project_id.start_time
            vals['date_start'] = _convert_to_utc_date(date_start, time, tz=tz)
        if (procurement.sale_line_id.order_id.project_id.date and
                procurement.sale_line_id.order_id.project_id.end_time):
            date_end = event_obj._convert_date_to_local_format(
                procurement.sale_line_id.order_id.project_id.date).date()
            time = procurement.sale_line_id.order_id.project_id.end_time
            vals['date_end'] = _convert_to_utc_date(date_end, time, tz=tz)
        return vals

    def _prepare_session_data_from_task(self, event, num_session, date):
        vals = super(ProjectTask, self)._prepare_session_data_from_task(
            event, num_session, date)
        account = self.service_project_sale_line.order_id.project_id
        vals.update({'date': event._put_utc_format_date(date,
                                                        account.start_time),
                     'type_hour': account.type_hour.id})
        return vals
