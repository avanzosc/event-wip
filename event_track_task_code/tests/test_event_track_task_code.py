# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventTrackTaskCode(common.TransactionCase):

    def setUp(self):
        super(TestEventTrackTaskCode, self).setUp()
        self.task = self.env['project.task'].create(
            {'name': 'Test event track task code',
             'code': 'TTTT-000021'})
        self.session = self.env['event.track'].search([], limit=1)
        self.session.task_id = self.task.id

    def test_event_track_task_code(self):
        self.session._compute_lit_task_code()
        self.assertEqual(
            self.session.lit_task_code, ', Task code: TTTT-000021',
            'Bad literal for task code in event track')
