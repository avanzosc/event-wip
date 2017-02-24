# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models
from openerp.addons.event_track_assistant._common import\
    _convert_to_utc_date, _convert_to_local_date


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _create_new_account_project_by_task(self, task, parent_account, code):
        account = super(ProjectTask, self)._create_new_account_project_by_task(
            task, parent_account, code)
        if parent_account.type_hour:
            account.type_hour = parent_account.type_hour.id
        return account

    def _account_info_for_create_task_service_project(self, vals, procurement):
        tz = self.env.user.tz
        vals = super(
            ProjectTask, self)._account_info_for_create_task_service_project(
            vals, procurement)
        project = procurement.sale_line_id.order_id.project_id
        if project.date_start and project.start_time:
            date_start = _convert_to_local_date(
                project.date_start, tz=tz).date()
            time = project.start_time
            vals['date_start'] = _convert_to_utc_date(date_start, time, tz=tz)
        if project.date and project.end_time:
            date_end = _convert_to_local_date(project.date, tz=tz).date()
            time = project.end_time
            vals['date_end'] = _convert_to_utc_date(date_end, time, tz=tz)
        return vals

    def _prepare_session_data_from_task(self, event, num_session, date):
        tz = self.env.user.tz
        vals = super(ProjectTask, self)._prepare_session_data_from_task(
            event, num_session, date)
        account = self.service_project_sale_line.order_id.project_id
        vals.update({
            'date': _convert_to_utc_date(date, account.start_time, tz=tz),
            'type_hour': account.type_hour.id,
        })
        return vals
