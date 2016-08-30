# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class HrContract(models.Model):
    _name = 'hr.contract'
    _inherit = ['hr.contract', 'mail.thread', 'ir.needaction_mixin']

    holiday_calendars = fields.Many2many(
        comodel_name='calendar.holiday', string='Holiday calendars')
    partner = fields.Many2one(
        comodel_name='res.partner', string='Contract employee',
        related='employee_id.address_home_id')
    calendar_days = fields.One2many(
        comodel_name='res.partner.calendar.day', inverse_name='contract',
        string='Employee calendar days')

    @api.model
    def create(self, vals):
        contract = super(HrContract, self).create(vals)
        if contract.partner:
            contract.message_subscribe(contract.partner.ids)
        return contract

    @api.multi
    def write(self, vals):
        result = super(HrContract, self).write(vals)
        for contract in self.filtered('partner'):
            contract.message_subscribe(contract.partner.ids)
        return result
