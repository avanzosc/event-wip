# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    replaces_to = fields.Many2one(
        comodel_name='res.partner', string='Replaces to')

    def _prepare_wizard_registration_open_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_registration_open_vals()
        wiz_vals.update({'replaces_to': self.replaces_to.id})
        return wiz_vals


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    replaced_by = fields.Many2one(
        comodel_name='res.partner', string='Replaced by')
    replaces_to = fields.Many2one(
        comodel_name='res.partner', string='Replaces to')
