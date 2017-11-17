# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def _generate_calendar_from_wizard(self, year):
        res = super(HrContract, self)._generate_calendar_from_wizard(year)
        presence_obj = self.env['event.track.presence']
        date_from = '{}-01-01'.format(year)
        date_to = '{}-12-31'.format(year)
        for contract in self:
            cond = [('partner', '=', contract.partner.id),
                    ('session_date_without_hour', '>=', date_from),
                    ('session_date_without_hour', '<=', date_to)]
            presences = presence_obj.search(cond)
            presences._calculate_partner_calendar_day()
        return res
