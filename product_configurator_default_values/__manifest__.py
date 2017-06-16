# -*- coding: utf-8 -*-

{
    'name': 'Product Configurator Default Values',
    'version': '10.0',
    'category': 'Generic Modules/Base',
    'summary': 'Get default values for product configuration',
    'description': """
        Default Value for Product Configurator
    """,
    'author': 'Microcom',
    'license': 'AGPL-3',
    'website': 'http://www.microcom.ca/',
    'depends': [
        'product_configurator',
        'product_configurator_wizard',
    ],
    "data": [
        'views/product_view.xml',
    ],
    'demo': [
    ],
    'images': [
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
