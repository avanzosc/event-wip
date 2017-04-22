# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def automatic_process_generate_calendar(self):
        contract_obj = self.env['hr.contract']
        wiz_obj = self.env['wiz.calculate.workable.festive']
        date_begin = '{}-01-01'.format(fields.Date.from_string(
            fields.Date.today()).year)
        cond = [('type_id', '=',
                 self.env.ref('hr_contract.hr_contract_type_emp').id),
                '|', ('date_end', '=', False),
                ('date_end', '>=', date_begin)]
        contracts = contract_obj.search(cond)
        if contracts:
            wiz = wiz_obj.create(
                {'year': fields.Date.from_string(fields.Date.today()).year})
        for contract in contracts:
            wiz.with_context(
                {'active_id':
                 contract.id}).button_calculate_workables_and_festives()
