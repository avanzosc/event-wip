# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, exceptions, _


class WizEventDeleteCanceledRegistration(models.TransientModel):
    _name = 'wiz.event.delete.canceled.registration'

    @api.multi
    def delete_canceled_registration(self):
        event_obj = self.env['event.event']
        for event in event_obj.browse(self.env.context.get('active_ids')):
            registrations = event.registration_ids.filtered(
                lambda x: x.state == 'cancel')
            presences = event.track_ids.mapped('presences')
            partners = registrations.mapped('partner_id')
            for partner in partners:
                if presences.filtered(lambda x: x.partner.id == partner.id and
                                      x.state != 'canceled'):
                    raise exceptions.Warning(
                        _("%s, has presences without canceling") %
                        partner.name)
            presences.filtered(lambda x: x.state == 'canceled').unlink()
            registrations_accounts = registrations.filtered(
                lambda x: x.analytic_account)
            accounts = registrations_accounts.mapped('analytic_account')
            accounts.unlink()
            registrations.write({'state': 'draft'})
            registrations.unlink()
