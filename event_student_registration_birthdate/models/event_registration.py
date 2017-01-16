# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, exceptions, _


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model
    def create(self, vals):
        partner_obj = self.env['res.partner']
        if vals.get('partner_id', False):
            partner = partner_obj.browse(vals.get('partner_id'))
            if not partner.employee_id and not partner.birthdate_date:
                raise exceptions.Warning(
                    _('You must define the birthdate for the student %s')
                    % (partner.name))
        registration = super(EventRegistration, self).create(vals)
        return registration
