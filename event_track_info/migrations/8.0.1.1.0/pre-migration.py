# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def update_field_names(cr):
    cr.execute(
        """
        ALTER TABLE product_event_track_template
        RENAME COLUMN product TO product_id;
        """)


def delete_views(cr):
    cr.execute(
        """
        DELETE FROM ir_ui_view
        WHERE id in (SELECT res_id
                     FROM ir_model_data
                     WHERE module = 'event_track_info'
                     AND model = 'ir.ui.view');
        """)
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = 'event_track_info'
        AND model = 'ir.ui.view';
        """)


def migrate(cr, version):
    if not version:
        return
    update_field_names(cr)
    delete_views(cr)
