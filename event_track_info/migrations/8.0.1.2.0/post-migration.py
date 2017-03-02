# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def assign_templates_in_product_event_track_template(cr):
    cr.execute("""UPDATE product_event_track_template
                  SET    product_tmpl_id = product_product.product_tmpl_id
                  FROM   product_product
                  WHERE  product_event_track_template.product_id =
                         product_product.id;
                  """)


def migrate(cr, version):
    if not version:
        return
    assign_templates_in_product_event_track_template(cr)
