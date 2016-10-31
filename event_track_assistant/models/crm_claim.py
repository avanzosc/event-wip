# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    event_id = fields.Many2one(comodel_name='event.event', string='Event')
    session_id = fields.Many2one(comodel_name='event.track', string='Session')
