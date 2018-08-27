# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    sale = fields.Many2one(comodel_name='sale.order', string='Sale Order')
    working_hours = fields.Many2one(
        comodel_name='resource.calendar', string='Working Schedule')
    event_id = fields.Many2one(comodel_name='event.event', string='Event')
    event_address_id = fields.Many2one(
        comodel_name='res.partner', string='Event address', store=True,
        related='event_id.address_id')
    event_organizer_id = fields.Many2one(
        comodel_name='res.partner', string='Event organizer', store=True,
        related='event_id.organizer_id')

    @api.multi
    def write(self, vals):
        if (self.env.context.get('without_sale_name', False) and
                vals.get('name', False)):
            vals.pop('name')
        return super(AccountAnalyticAccount, self).write(vals)

    @api.multi
    def _recalculate_sessions_date_from_calendar(self):
        event_obj = self.env['event.event']
        for account in self.filtered(lambda x: x.working_hours):
            cond = [('sale_order', '=', account.sale.id)]
            events = event_obj.search(cond)
            for hour in account.working_hours.attendance_ids:
                for event in events:
                    date = hour.date_from or account.date_start
                    for session in event.mapped('track_ids').filtered(
                        lambda x: x.day == hour.dayofweek and
                            x.session_date >= date):
                        new_date, duration = (
                            account.working_hours._calc_date_and_duration(
                                fields.Datetime.from_string(
                                    session.session_date)))
                        if new_date:
                            session.write({'date': new_date,
                                           'duration': duration})
