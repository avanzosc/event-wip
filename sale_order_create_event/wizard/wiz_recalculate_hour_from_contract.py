# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizRecalculateHourFromContract(models.TransientModel):
    _name = 'wiz.recalculate.hour.from.contract'

    name = fields.Char(
        string='Days', default="Recalculate hour from contract")

    @api.multi
    def recalculate_session_date(self):
        self.ensure_one()
        account_obj = self.env['account.analytic.account']
        accounts = account_obj.browse(
            self.env.context.get('active_ids')).filtered(
            lambda x: x.sale and x.working_hours)
        accounts._recalculate_sessions_date_from_calendar()
