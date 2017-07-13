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
        event_obj = self.env['event.event']
        accounts = account_obj.browse(
            self.env.context.get('active_ids')).filtered(
            lambda x: x.sale and x.working_hours)
        for account in accounts:
            cond = [('sale_order', '=', account.sale.id)]
            events = event_obj.search(cond)
            for session in events.mapped('track_ids'):
                new_date, duration = (
                    account.working_hours._calc_date_and_duration(
                        fields.Datetime.from_string(session.session_date)))
                if new_date:
                    session.write({'date': new_date,
                                   'duration': duration})
