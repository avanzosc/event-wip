# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestHrContractCalendarScheduler(common.TransactionCase):

    def setUp(self):
        super(TestHrContractCalendarScheduler, self).setUp()
        self.contract_model = self.env['hr.contract']
        self.calendar_model = self.env['res.partner.calendar']
        contract_vals = {'name': 'Contract 1',
                         'employee_id': self.ref('hr.employee_vad'),
                         'partner': self.ref('base.public_partner'),
                         'type_id':
                         self.ref('hr_contract.hr_contract_type_emp'),
                         'wage': 500,
                         'date_start': '2010-02-01',
                         'working_hours':
                         self.ref('resource.timesheet_group1')}
        self.contract = self.contract_model.create(contract_vals)

    def test_hr_contract_calendar_Scheduler(self):
        self.contract.automatic_process_generate_calendar()
        cond = [('partner', '=', self.ref('base.public_partner'))]
        calendars = self.calendar_model.search(cond)
        self.assertEquals(
            len(calendars), 1, 'Calendar no generated for employee')
