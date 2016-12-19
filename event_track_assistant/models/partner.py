# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('session_ids')
    def _compute_session_count(self):
        for partner in self:
            partner.session_count = len(partner.session_ids)

    @api.multi
    @api.depends('presence_ids')
    def _compute_presences_count(self):
        for partner in self:
            partner.presence_count = len(partner.presence_ids)

    session_ids = fields.Many2many(
        comodel_name="event.track", relation="rel_partner_event_track",
        column1="partner_id", column2="event_track_id", string="Sessions",
        copy=False)
    session_count = fields.Integer(
        string='# Sessions', compute='_compute_session_count',
        store=True)
    presence_ids = fields.One2many(
        comodel_name='event.track.presence', inverse_name='partner',
        string='Presences')
    presence_count = fields.Integer(
        string='# Presences', compute='_compute_presences_count',
        store=True)

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
