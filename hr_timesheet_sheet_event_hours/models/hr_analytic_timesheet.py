# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    festive = fields.Boolean(string='Festive', default=False)
