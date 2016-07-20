# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class EventTrack(models.Model):
    _inherit = 'event.track'

    planification = fields.Text(string="Planification")
    resolution = fields.Text(string="Resolution")
    url = fields.Char(string='URL')
