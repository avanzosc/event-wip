# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizRegistrationToAnotherEvent(models.TransientModel):
    _name = 'wiz.registration.to.another.event'

    event_registration_id = fields.Many2one(
        string='Registration', comodel_name='event.registration')
    event_id = fields.Many2one(
        string='Actual event of registration', comodel_name='event.event',
        readonly=True)
    new_event_id = fields.Many2one(
        string='New event for the registration', comodel_name='event.event',
        required=True)

    @api.model
    def default_get(self, var_fields):
        res = super(
            WizRegistrationToAnotherEvent, self).default_get(var_fields)
        registration = self.env['event.registration'].browse(
            self.env.context['active_id'])
        res.update({
            'event_registration_id': registration.id,
            'event_id': registration.event_id.id,
        })
        return res

    @api.multi
    def button_change_registration_event(self):
        self.event_id.mapped('track_ids.presences').filtered(
            lambda x: x.partner == self.event_registration_id.partner_id and
            x.state == 'pending').button_canceled()
        self._change_registration_event()
        if self.event_registration_id.state == 'open':
            self.event_registration_id.state = 'draft'
            return self.event_registration_id.button_registration_open()

    def _change_registration_event(self):
        self.event_registration_id.write({
            'event_id': self.new_event_id.id,
            'date_start': self.new_event_id.date_begin,
            'date_end': self.new_event_id.date_end,
        })
