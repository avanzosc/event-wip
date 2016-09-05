# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class WizEventConfirmAssistant(models.TransientModel):
    _inherit = 'wiz.event.confirm.assistant'

    def _prepare_data_confirm_assistant(self, reg):
        session_obj = self.env['event.track']
        event_obj = self.env['event.event']
        tasks = self.env['project.task']
        append_vals = super(WizEventConfirmAssistant,
                            self)._prepare_data_confirm_assistant(reg)
        from_date = event_obj._convert_date_to_local_format(
            reg.date_start).date()
        from_date = fields.Datetime.to_string(
            event_obj._put_utc_format_date(from_date, 0.0))
        to_date = event_obj._convert_date_to_local_format(reg.date_end).date()
        to_date = fields.Datetime.to_string(
            event_obj._put_utc_format_date(to_date, 0.0))
        cond = [('event_id', '=', reg.event_id.id),
                ('date', '>=', from_date),
                ('date', '<=', to_date),
                ('date', '!=', False)]
        sessions = session_obj.search(cond)
        tasks = sessions.mapped('tasks')
        append_vals.update({'permitted_tasks': [(6, 0, tasks.ids)],
                            'tasks': [(6, 0, tasks.ids)]})
        return append_vals
