# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions


class TestTypeHour(common.TransactionCase):

    def setUp(self):
        super(TestTypeHour, self).setUp()
        self.type_hour_model = self.env['hr.type.hour'].with_context(
            check_write_type_hour=True)
        self.sunday = self.browse_ref(
            'sale_order_create_event_hour.type_hour_sunday').with_context(
            check_write_type_hour=True)

    def test_disabled_editing_module_type_hour(self):
        with self.assertRaises(exceptions.Warning):
            self.sunday.name = 'SUNDAY'
        with self.assertRaises(exceptions.Warning):
            self.sunday.unlink()

    def test_type_hour(self):
        hour_type = self.type_hour_model.create({
            'name': 'Test',
        })
        hour_type.name = 'New Name'
        hour_type.unlink()
