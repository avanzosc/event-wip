# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    validate_mandate = fields.Boolean(
        string='Validate exists mandate', default=True)
