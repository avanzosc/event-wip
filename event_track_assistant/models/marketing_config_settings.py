# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class MarketingConfigSettings(models.Model):
    _inherit = 'marketing.config.settings'

    show_all_customers_in_presences = fields.Boolean(
        string='Show all customers in presences')

    def _get_parameter(self, key, default=False):
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', key)])
        return rec or default

    def _write_or_create_param(self, key, value):
        param_obj = self.env['ir.config_parameter']
        rec = self._get_parameter(key)
        if rec:
            if not value:
                rec.unlink()
            else:
                rec.value = value
        elif value:
            param_obj.create({'key': key, 'value': value})

    @api.multi
    def get_default_parameters(self):
        def get_value(key, default=''):
            rec = self._get_parameter(key)
            return rec and rec.value or default
        return {
            'show_all_customers_in_presences':
            get_value('show.all.customers.in.presences', False)}

    @api.multi
    def set_parameters(self):
        self._write_or_create_param('show.all.customers.in.presences',
                                    self.show_all_customers_in_presences)
