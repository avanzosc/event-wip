# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, fields, exceptions, models
from openerp.tools import config


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
            mandates = partner_id.mapped('bank_ids.mandate_ids').filtered(
                lambda x: x.format == 'sepa')
            record.sepa_active = len(mandates.filtered(
                lambda x: x.state == 'valid'))
            record.sepa_draft = len(mandates.filtered(
                lambda x: x.state == 'draft'))

    @api.multi
    def registration_open(self):
        if (config['test_enable'] and
                not self.env.context.get('check_mandate_sepa')):
            return super(EventRegistration, self).registration_open()
        if (self.event_id.sale_order.payer == 'student' and
                self.sepa_active == 0 and not self.partner_id.employee_id):
            raise exceptions.Warning(
                _('%s needs a valid sepa mandate for confirm the assistant!')
                % self.partner_id.name)
        return super(EventRegistration, self).registration_open()

    sepa_active = fields.Integer(compute='_compute_sepa', store=True)
    sepa_draft = fields.Integer(compute='_compute_sepa', store=True)
