# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def assign_product_training_plan(cr):
    cr.execute("""INSERT INTO training_plan
               (name, planification, resolution, html_info, url)
               select distinct name, planification, resolution, html_info, url
               from product_event_track_template;""")
    cr.execute("""INSERT INTO product_training_plan
                  (product_tmpl_id, product_id, sequence, training_plan_id)
                  select t.product_tmpl_id, t.product_id, t.sequence , p.id
                from product_event_track_template as t,
                     training_plan as p
                where t.name = p.name
                and (t.planification = p.planification or
                     t.planification is null);""")
    cr.execute("""DROP TABLE product_event_track_template;""")


def migrate(cr, version):
    if not version:
        return
    assign_product_training_plan(cr)
