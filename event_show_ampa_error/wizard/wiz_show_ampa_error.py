# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _


class WizShowAmpaError(models.TransientModel):
    _name = 'wiz.show.ampa.error'

    lines = fields.One2many(
        comodel_name='wiz.show.ampa.error.line',
        inverse_name='wiz_id', string='Presences')

    @api.model
    def default_get(self, var_fields):
        registration_obj = self.env['event.registration']
        vals = []
        cond = [('state', '=', 'open'),
                ('employee', '=', False),
                ('analytic_account', '!=', False)]
        registrations = registration_obj.search(cond)
        for reg in registrations.filtered(lambda x: x.parent_id.is_pa_partner
                                          and x.event_id.sale_order.payer ==
                                          'student'):
            lines = reg.event_id.event_ticket_ids.filtered(
                lambda x: x.is_pa_partner == reg.parent_id.is_pa_partner)
            if not lines:
                raise exceptions.Warning(
                    _('Ticket not found for %s, in event: %s') % (reg.partner_id.name, reg.event_id.name))
            p = reg.analytic_account.recurring_invoice_line_ids[0].price_unit
            if lines[0].price != p:
                line_vals = {'event': reg.event_id.id,
                             'registration': reg.id,
                             'partner_id': reg.partner_id.id,
                             'account': reg.analytic_account.id,
                             'bad_price': p,
                             'ok_price': lines[0].price}
                vals.append(line_vals)
        return {'lines': vals}


class WizShowAmpaErrorLine(models.TransientModel):
    _name = 'wiz.show.ampa.error.line'

    wiz_id = fields.Many2one(
        comodel_name='wiz.show.ampa.error', string='Wizard')
    event = fields.Many2one('event.event', string='Event')
    registration = fields.Many2one(
        'event.registration', string='Registration')
    partner_id = fields.Many2one('res.partner', string="Student")
    account = fields.Many2one(
        'account.analytic.account', string='Analytic account')
    bad_price = fields.Float(string='Bad price')
    ok_price = fields.Float(string='OK price')
