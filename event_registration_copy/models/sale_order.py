# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    old_sale_order_id = fields.Many2one(
        comodel_name='sale.order', copy=False)

    @api.multi
    def action_button_confirm(self):
        wiz_obj = self.env['wiz.event.confirm.assistant']
        event_obj = self.env['event.event']
        res = super(SaleOrder, self).action_button_confirm()
        if self.old_sale_order_id and self.project_by_task == 'no':
            old_project = self.old_sale_order_id.project_id
            self.project_id.name = old_project.name.replace(
                str(fields.Date.from_string(old_project.date).year),
                str(fields.Date.from_string(self.project_id.date).year))
            if (old_project.recurring_invoices and
                old_project.recurring_rule_type == 'monthly' and
                    old_project.recurring_interval > 1):
                self.project_id.recurring_next_date = (
                    old_project.recurring_next_date)
            new_event = self._create_registrations_in_new_event()
            new_event = event_obj.browse(new_event.id)
            wiz = wiz_obj.create({})
            wiz.permitted_tasks = [(6, 0, new_event.task_ids.ids)]
            wiz.tasks = [(6, 0, new_event.task_ids.ids)]
            wiz.with_context(
                {'active_ids': [new_event.id]}).action_confirm_assistant()
        return res

    def _create_registrations_in_new_event(self):
        event_obj = self.env['event.event']
        registration_obj = self.env['event.registration']
        registrations = self._search_old_event_registrations(
            self.old_sale_order_id)
        cond = [('sale_order', '=', self.id)]
        new_event = event_obj.search(cond, limit=1)
        for registration in registrations:
            vals = self._catch_old_registration_information(registration)
            vals.update({'event_id': new_event.id,
                         'date_start': new_event.date_begin,
                         'date_end': new_event.date_end})
            registration_obj.create(vals)._find_contracts_for_employee()
        return new_event

    def _search_old_event_registrations(self, old_sale):
        event_obj = self.env['event.event']
        cond = [('sale_order', '=', old_sale.id)]
        old_event = event_obj.search(cond, limit=1)
        registrations = old_event.registration_ids.filtered(
            lambda x: x.state not in ('draft', 'cancel') and not x.replaces_to)
        return registrations

    def _catch_old_registration_information(self, registration):
        vals = {'partner_id': registration.partner_id.id,
                'name': registration.name,
                'email': registration.partner_id.email,
                'phone': registration.partner_id.phone}
        return vals

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['old_sale_order_id'] = self.id
        return super(SaleOrder, self).copy(default)
