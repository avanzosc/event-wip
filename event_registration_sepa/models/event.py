# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, exceptions, models
from openerp.tools import config


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.multi
    def registration_open(self):
        if (config['test_enable'] and
                not self.env.context.get('check_mandate_sepa')):
            return super(EventRegistration, self).registration_open()
        parent = self.partner_id.parent_id
        if ((not self.event_id.sale_order.payment_mode_id or
             self.event_id.sale_order.payment_mode_id.validate_mandate) and
            (not parent.customer_payment_mode or
             parent.customer_payment_mode.validate_mandate) and
            (self.event_id.sale_order.payer == 'student' and
             self.parent_num_valid_mandates == 0 and not
             self.partner_id.employee_id)):
            raise exceptions.Warning(
                _('%s needs a valid sepa mandate for confirm the assistant!')
                % self.partner_id.name)
        return super(EventRegistration, self).registration_open()
