# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, fields, exceptions, models


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
                    lambda x: x.state == 'valid' and x.format == 'sepa'))
            record.sepa_draft = len(
                partner_id.bank_ids.mapped('mandate_ids').filtered(
                    lambda x: x.state == 'draft' and x.format == 'sepa'))

    @api.multi
    def registration_open(self):
        partner_id = self.partner_id.parent_id or self.partner_id
        if not partner_id.bank_ids.mapped('mandate_ids').filtered(
                lambda x: x.state == 'valid' and x.format == 'sepa'):
            raise exceptions.Warning(
                _('%s needs a valid sepa mandate for confirm the assistant!')
                % self.partner_id.name)
        return super(EventRegistration, self).registration_open()

    address_id = fields.Many2one(
        comodel_name='res.partner', related='event_id.address_id', store=True)
    sepa_active = fields.Integer(compute='_compute_sepa', store=True)
    sepa_draft = fields.Integer(compute='_compute_sepa', store=True)
