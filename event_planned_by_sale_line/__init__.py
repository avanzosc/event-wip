# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from . import wizard
from . import models
from . import report
from openerp import SUPERUSER_ID


def fill_charge_information_is_sales(cr, registry):
    sale_obj = registry['sale.order']
    sale_ids = sale_obj.search(cr, SUPERUSER_ID, [])
    for sale in sale_obj.browse(cr, SUPERUSER_ID, sale_ids):
        if not sale.payer:
            try:
                vals = {'project_by_task': 'yes',
                        'product_category': 1,
                        'payer': 'student'}
                sale_obj.write(cr, SUPERUSER_ID, sale.id, vals)
            except:
                continue
