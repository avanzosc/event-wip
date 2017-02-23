# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api
from .._common import _convert_to_local_date, _convert_to_utc_date


class WizChangeSessionHour(models.TransientModel):
    _name = 'wiz.change.session.hour'

    new_hour = fields.Float(string='New hour', required=True)

    @api.multi
    def change_session_hour(self):
        self.ensure_one()
        tz = self.env.user.tz
        sessions = self.env['event.track'].browse(
            self.env.context.get('active_ids'))
        for session in sessions:
            new_date = _convert_to_local_date(session.date, tz=tz)
            utc_dt = _convert_to_utc_date(new_date, time=self.new_hour, tz=tz)
            session.date = utc_dt
