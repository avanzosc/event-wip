# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, exceptions, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for sale in self:
            sale_lines = sale.order_line.filtered(
                lambda x: x.recurring_service)
            lines = sale_lines.filtered(
                lambda x: not x.end_date and not x.session_number)
            if lines:
                bad_lines = ''
                for line in lines:
                    bad_lines += '{}, '.format(line.name)
                    raise exceptions.Warning(
                        _("You must enter the number of sessions, or the end"
                          " date, for lines: '%s'") % (bad_lines))
            lines = sale_lines.filtered(lambda x: x.session_number > 0)
            self._generate_lines_end_date(lines)
        return super(SaleOrder, self).action_button_confirm()
