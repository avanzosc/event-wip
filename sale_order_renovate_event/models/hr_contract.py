# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def automatic_process_generate_calendar(self):
        print ('11111111111111 inicio tratamiento')
        cron_renovate_event_contract = self.env.ref(
            'sale_order_renovate_event.ir_cron_renovate_contract_event_action')
        cron_renovate_event_contract.active = False
        self.env.cr.commit()
        contract_obj = self.env['hr.contract']
        date_begin = '{}-01-01'.format(fields.Date.from_string(
            fields.Date.today()).year)
        date_begin = '2022-01-01'
        cond = ['|', ('date_end', '=', False),
                ('date_end', '>=', date_begin)]
        contracts = contract_obj.search(cond)
        contador = 0
        for contract in contracts:
            contador += 1
            print ('11111 trato contrato: ' + str(contador) + ', de: ' + str(len(contracts)) + ', id contrato: ' + str(contract.id))
            contract._generate_calendar_from_wizard(
                2022)
#            fields.Date.from_string(fields.Date.today()).year)
        print ('111111 contador: ' + str(contador))
        print ('111111 total contratos: ' + str(len(contracts)))
        if contador > 0 and contador == len(contracts):
            print ('111 entro en if')
            cron_renovate_event_contract.active = True
        print ('1111111111111111111 fin del tratamiento')
