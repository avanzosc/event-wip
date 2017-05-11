# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, exceptions, _
from openerp.addons.event_track_assistant._common import\
    _convert_to_local_date, _convert_to_utc_date

datetime2str = fields.Datetime.to_string


class WizEventConfirmAssistant(models.TransientModel):
    _inherit = 'wiz.event.confirm.assistant'

    def _prepare_data_confirm_assistant(self, reg):
        session_obj = self.env['event.track']
        tz = self.env.user.tz
        tasks = self.env['project.task']
        append_vals = super(WizEventConfirmAssistant,
                            self)._prepare_data_confirm_assistant(reg)
        from_date = _convert_to_local_date(reg.date_start, tz=tz).date()
        from_date = datetime2str(_convert_to_utc_date(from_date, 0.0, tz=tz))
        to_date = _convert_to_local_date(reg.date_end, tz=tz).date()
        to_date = datetime2str(_convert_to_utc_date(to_date, 0.0, tz=tz))
        cond = [('event_id', '=', reg.event_id.id),
                ('date', '>=', from_date),
                ('date', '<=', to_date),
                ('date', '!=', False)]
        sessions = session_obj.search(cond)
        tasks = sessions.mapped('tasks')
        if not tasks:
            raise exceptions.Warning(_("It was not found any task"))
        append_vals.update({'permitted_tasks': [(6, 0, tasks.ids)],
                            'tasks': [(6, 0, tasks.ids)]})
        return append_vals
