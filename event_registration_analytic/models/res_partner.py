# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    parent_is_company = fields.Boolean(
        'Parent is company', related='parent_id.is_company', store=True)
    parent_is_group = fields.Boolean(
        'Parent is group', related='parent_id.is_group', store=True)
