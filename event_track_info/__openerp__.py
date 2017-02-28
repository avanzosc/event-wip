# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Event Track Info",
    "version": "8.0.1.2.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es",
    ],
    "category": "Event Management",
    "depends": [
        "product",
        "event_sale",
        "event_report",
        "website_event_track",
        "event_track_assistant",
        "sale_order_create_event"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/event_track_view.xml",
        "views/product_product_view.xml",
        "views/product_event_track_template_view.xml",
    ],
    "installable": True,
}
