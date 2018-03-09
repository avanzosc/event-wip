# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    substitution_presences = fields.Many2many(
        comodel_name='event.track.presence', string='Substitution presences')

    @api.multi
    def _send_email_to_employees_substitution(self, replaces_to, replaced_by,
                                              presences):
        mail_template = self.env.ref(
            'event_substitution.email_to_workers_by_substitution', False)
        if mail_template:
            partners = self.env['res.partner']
            if replaces_to.email:
                partners += replaces_to
            if replaced_by.email:
                partners += replaced_by
            if self.user_id.partner_id.email:
                partners += self.user_id.partner_id
            if partners:
                self._send_email_by_substitution(mail_template, partners,
                                                 presences)

    def _send_email_by_substitution(self, template, partners, presences):
        self.substitution_presences = [(6, 0, presences.ids)]
        mail = self.env['mail.compose.message'].with_context(
            default_composition_mode='mass_mail',
            default_template_id=template.id,
            default_use_template=True,
            default_partner_ids=[(6, 0, partners.ids)],
            active_id=self.id,
            active_ids=self.ids,
            active_model='event.event',
            default_model='event.event',
            default_res_id=self.id,
            force_send=True
        ).create({'subject': template.subject,
                  'body': template.body_html})
        mail.send_mail()


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

    @api.multi
    def _compute_session_date_without_hour_located(self):
        for presence in self:
            date = fields.Date.from_string(presence.session_date_without_hour)
            presence.session_date_without_hour_located = (
                date.strftime('%d-%m-%Y'))

    replaced_by = fields.Many2one(
        comodel_name='res.partner', string='Replaced by')
    replaces_to = fields.Many2one(
        comodel_name='res.partner', string='Replaces to')
    session_date_without_hour_located = fields.Char(
        string='Session date located',
        compute='_compute_session_date_without_hour_located')
