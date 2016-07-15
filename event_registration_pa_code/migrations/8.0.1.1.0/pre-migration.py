# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_columns(cr):
    cr.execute(
        """
        ALTER TABLE res_partner
        RENAME COLUMN pa_partner TO is_pa_partner
        """)
    cr.execute(
        """
        ALTER TABLE event_event_ticket
        RENAME COLUMN pa_partner TO is_pa_partner
        """)
    cr.execute(
        """
        ALTER TABLE res_partner
        RENAME COLUMN partner_product_ul TO partner_product_ul_id
        """)


def migrate(cr, version):
    if not version:
        return
    update_columns(cr)
