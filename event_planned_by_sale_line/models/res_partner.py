# -*- coding: utf-8 -*-
# Copyright 2017 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models, api


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _get_selection_payer(self):
        return self.env['sale.order'].fields_get(allfields=['payer']
                                                 )['payer']['selection']

    payer = fields.Selection(string='Payer', selection='_get_selection_payer')
