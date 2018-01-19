# -*- coding: utf-8 -*-
{
    'name': "Product Configurator Step restriction",

    'summary': """
Allow to skip a configuration step""",

    'description': """
Add a restriction on the step to skip it""",

    'category': 'sale_stock',
    'version': '11.0',
    'author': 'Microcom',
    'website': 'http://www.microcom.ca/',

    'depends': ['product_configurator_wizard'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/scenario_views.xml',
        'views/product_config_view.xml',
    ],

    'demo': [
        'demo/scenario_attributes.xml',
    ],
}
