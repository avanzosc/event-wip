# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


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

    @api.multi
    def _send_email_to_employees_substitution(self):
        mail_template = self.env.ref(
            'event_substitution.email_to_workers_by_substitution', False)
        if mail_template:
            for presence in self:
                if presence.partner.email:
                    presence._send_email_by_substitution(
                        mail_template, presence.partner)
                if presence.replaced_by.email:
                    presence._send_email_by_substitution(
                        mail_template, presence.replaced_by)
                if presence.event.user_id.partner_id.email:
                    presence._send_email_by_substitution(
                        mail_template, presence.event.user_id.partner_id)

    def _send_email_by_substitution(self, template, partner):
        mail = self.env['mail.compose.message'].with_context(
            default_composition_mode='mass_mail',
            default_template_id=template.id,
            default_use_template=True,
            active_id=self.id,
            active_ids=self.ids,
            active_model='event.track.presence',
            default_model='event.track.presence',
            default_res_id=self.id,
            force_send=True
        ).create({'body': template.body_html})
        mail.partner_ids = [(6, 0, partner.ids)]
        mail.send_mail()
