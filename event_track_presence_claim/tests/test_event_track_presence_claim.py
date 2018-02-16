# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta


class TestEventTrackPresenceClaim(common.TransactionCase):

    def setUp(self):
        super(TestEventTrackPresenceClaim, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Partner for test crm claim event presence'})
        self.employee = self.browse_ref('hr.employee_al')
        self.employee.address_home_id = self.partner.id
        contract_vals = {'name': 'New contract for employee',
                         'employee_id': self.employee.id,
                         'wage': 1000,
                         'date_start': '2018-01-01'}
        self.contract = self.env['hr.contract'].create(contract_vals)
        today = fields.Date.today()
        date_end = '{} 12:00:00'.format(today)
        date_begin = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=-4))
        date_begin = '{} 10:00:00'.format(date_begin)
        tracks = []
        contador = 0
        while contador < 5:
            track = {'name': date_begin,
                     'date': date_begin,
                     'duration': 2,
                     'presences': [(0, 0, {'partner': self.partner.id,
                                           'name': self.partner.name,
                                           'session_duration': 2,
                                           'session_date': date_begin,
                                           'contract': self.contract.id,
                                           'employee': self.employee.id,
                                           'employee_id': self.employee.id})]}
            tracks.append((0, 0, track))
            date_begin = fields.Date.to_string(fields.Date.from_string(
                date_begin) + relativedelta(days=1))
            date_begin = '{} 10:00:00'.format(date_begin)
            contador += 1
        date_begin = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=-4))
        event_vals = {'name': 'Test crm claim event presence',
                      'date_begin': date_begin,
                      'date_end': date_end,
                      'warnings_not_imputations_count': 2,
                      'track_ids': tracks}
        self.event = self.env['event.event'].create(event_vals)

    def test_event_track_presence_claim(self):
        self.env['event.track']._search_no_imputations_and_create_claim()
        cond = [('event_id', '=', self.event.id)]
        claims = self.env['crm.claim'].search(cond)
        self.assertEqual(len(claims), 3, 'Claims not found')
