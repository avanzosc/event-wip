# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_session_count(self):
        for partner in self:
            partner.session_count = len(partner.session_ids)

    @api.multi
    def _compute_presences_count(self):
        for partner in self:
            partner.presences_count = len(partner.presence_ids)

    session_ids = fields.Many2many(
        comodel_name="event.track", relation="rel_partner_event_track",
        column1="partner_id", column2="event_track_id", string="Sessions",
        copy=False)
    session_count = fields.Integer(
        string='Sessions counter', compute='_compute_session_count')
    presence_ids = fields.One2many(
        comodel_name='event.track.presence', inverse_name='partner',
        string='Presences')
    presences_count = fields.Integer(
        string='Presences counter', compute='_compute_presences_count')
    registered_partner = fields.Boolean(
        string='Registered Partner', compute='_compute_registered_partner',
        default=False, store=True)

    @api.depends('registrations')
    def _compute_registered_partner(self):
        for partner in self:
            partner.registered_partner = (len(partner.registrations) != 0)

    @api.multi
    def show_sessions_from_partner(self):
        res = {'view_mode': 'kanban,tree,form,calendar,graph',
               'res_model': 'event.track',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'domain': [('id', 'in', self.mapped('session_ids').ids)]}
        return res

    @api.multi
    def show_presences_from_partner(self):
        res = {'view_mode': 'tree,form',
               'res_model': 'event.track.presence',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'domain': [('partner', '=', self.id)]}
        return res
