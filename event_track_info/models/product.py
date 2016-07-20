# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    event_track_templates = fields.One2many(
        comodel_name='product.event.track.template', inverse_name='product',
        string='Event track templates')


class ProductEventTrackTemplate(models.Model):
    _name = 'product.event.track.template'
    _description = 'Templates for event track'
    _rec_name = 'product'
    _order = 'product, sequence asc'

    product = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    sequence = fields.Integer(string="Sequence", required=True)
    planification = fields.Text(string="Planification")
    resolution = fields.Text(string="Resolution")
    html_info = fields.Html(string='Description', translate=True)
    url = fields.Char(string='URL')
