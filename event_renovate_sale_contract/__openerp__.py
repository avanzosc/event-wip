# -*- coding: utf-8 -*-
# Copyright 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Event Renovate Sale Contract",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    "category": "Sales Management",
    "depends": [
        "sale_order_renovate_contract",
        "sale_order_create_event"
    ],
    "data": [
        "views/account_analytic_account_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
