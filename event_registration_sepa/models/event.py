# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.multi
    @api.depends('partner_id', 'partner_id.parent_id',
                 'partner_id.parent_id.bank_ids',
                 'partner_id.parent_id.bank_ids.mandate_ids',
                 'partner_id.parent_id.bank_ids.mandate_ids.state')
    def _compute_sepa(self):
        for record in self:
            partner_id = record.partner_id.parent_id or record.partner_id
            record.sepa_active = len(
                partner_id.bank_ids.mapped('mandate_ids').filtered(
                    lambda x: x.state == 'valid'))
            record.sepa_draft = len(
                partner_id.bank_ids.mapped('mandate_ids').filtered(
                    lambda x: x.state == 'draft'))

    address_id = fields.Many2one(
        comodel_name='res.partner', related='event_id.address_id', store=True)
    sepa_active = fields.Integer(compute='_compute_sepa', store=True)
    sepa_draft = fields.Integer(compute='_compute_sepa', store=True)
