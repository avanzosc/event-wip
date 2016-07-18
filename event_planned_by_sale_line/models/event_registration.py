# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, exceptions, _


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model
    def create(self, vals):
        event_obj = self.env['event.event']
        partner_obj = self.env['res.partner']
        if vals.get('event_id', False) and vals.get('partner_id', False):
            event = event_obj.browse(vals.get('event_id'))
            partner = partner_obj.browse(vals.get('partner_id'))
            if not partner.is_group and not partner.is_company:
                if event.sale_order.payer == 'school':
                    partner.parent_id = event.address_id.id
                else:
                    if not partner.parent_id:
                        raise exceptions.Warning(
                            _('Yoy must define the company for the student %s')
                            % (partner.name))
        registration = super(EventRegistration, self).create(vals)
        return registration
