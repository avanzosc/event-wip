# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, exceptions, models


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    @api.multi
    def action_append(self):
        partner_id = self.partner.parent_id or self.partner
        if not partner_id.bank_ids.mapped('mandate_ids').filtered(
                lambda x: x.state == 'valid' and x.format == 'sepa'):
            raise exceptions.Warning(
                _('%s needs a valid sepa mandate for confirm the assistant!')
                % self.partner.name)
        return super(WizEventAppendAssistant, self).action_append()
