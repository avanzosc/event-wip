# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta
str2datetime = fields.Datetime.from_string
str2date = fields.Date.from_string
datetime2str = fields.Datetime.to_string
date2str = fields.Date.to_string


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def write(self, values):
        expired_stage = self.env.ref(
            'hr_contract_stages.stage_contract3', False)
        res = super(HrContract, self).write(values)
        if (values.get('contract_stage_id', False) and expired_stage and
                values.get('contract_stage_id') == expired_stage.id):
            for contract in self:
                if not contract.date_end:
                    raise exceptions.Warning(
                        _("You must enter the end date of the contract: %s") %
                        contract.name)
                contract._close_event_registrations_and_presences()
        return res

    def _close_event_registrations_and_presences(self):
        contract_date_end = (fields.Date.from_string(self.date_end) +
                             relativedelta(days=+1))
        cond = [('partner_id', '=', self.partner.id),
                ('contract', '=', self.id),
                ('state', 'not in', ('cancel', 'done')),
                ('date_end', '>=', date2str(contract_date_end))]
        registrations = self.env['event.registration'].search(cond)
        for registration in registrations:
            reg_date_start = str2datetime(registration.date_start)
            from_date = (contract_date_end if contract_date_end >
                         reg_date_start.date() else reg_date_start.date())
            from_date = date2str(from_date)
            to_date = str2datetime(registration.date_end).date()
            to_date = date2str(to_date)
            registration._cancel_registration(
                from_date, to_date, fields.Date.context_today(self),
                _('Cancellation by contract termination'))
