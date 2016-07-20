# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizImputeInPresenceFromSession(models.TransientModel):
    _inherit = 'wiz.impute.in.presence.from.session'

    @api.model
    def default_get(self, var_fields):
        partner_obj = self.env['res.partner']
        res = super(WizImputeInPresenceFromSession,
                    self).default_get(var_fields)
        lines = res.get('lines', False)
        for line in lines:
            if line.get('partner', False):
                partner = partner_obj.browse(line.get('partner'))
                if partner.employee_id:
                    line['employee'] = partner.employee_id.id
        return res


class WizImputeInPresenceFromSessionLine(models.TransientModel):
    _inherit = 'wiz.impute.in.presence.from.session.line'

    employee = fields.Many2one(
        comodel_name='hr.employee', string='Employee')
