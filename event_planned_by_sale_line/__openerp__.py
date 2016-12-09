# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Event Planned By Sale Line",
    "version": "8.0.1.0.0",
    "category": "Custom Module",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es",
    ],
    "depends": [
        "sale_stock",
        "sale_stock_product_variants",
        "sale_service_recurrence_configurator",
        "sale_order_line_performance",
        "event_registration_analytic",
        "website_quote",
        "sale_product_variants",
        "account_analytic_analysis_recurring_day",
        "account_analytic_invoice_line_menu"
    ],
    "data": [
        "views/product_template_view.xml",
        "views/sale_order_view.xml",
        "views/product_category_view.xml",
        "views/account_analytic_invoice_line_view.xml",
    ],
    "installable": True,
    "post_init_hook": "fill_charge_information_is_sales",
}
