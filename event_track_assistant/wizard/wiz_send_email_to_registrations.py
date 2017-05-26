# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _


class WizSendEmailToRegistrations(models.TransientModel):
    _name = 'wiz.send.email.to.registrations'
    _description = 'Wizard for send email to event registrations'

    body = fields.Html(string='Email body')

    @api.model
    def default_get(self, var_fields):
        res = super(WizSendEmailToRegistrations, self).default_get(var_fields)
        template = self.env.ref(
            'event_registration_mass_mailing.email_template_event_'
            'registration', False)
        if not template:
            raise exceptions.Warning(
                _("Email template not found for event registration"))
        res.update({'body': template.body_html})
        return res

    @api.multi
    def button_send_email(self):
        self.env['event.event'].browse(self.env.context.get(
            'active_id'))._send_email_to_registrations(self.body)
