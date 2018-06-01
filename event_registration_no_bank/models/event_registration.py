# -*- coding: utf-8 -*-
# Copyright Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def show_sepa_mandate_error(self):
        pass
