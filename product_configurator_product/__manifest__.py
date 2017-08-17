{
    'name': 'Product Configurator Wizard for Products',
    'category': 'Product',
    'summary': 'This module allows to create and modify variants using the configurator wizard',
    'website': 'http://www.microcom.ca',
    'version': '10.0',
    'description': """
This module allows to create and modify variants using the configurator wizard.
===============================================================================

        """,
    'author': 'Microcom',
    'depends': ['product', 'product_configurator', 'product_configurator_wizard'],
    'data': [
        'views/product_views.xml',
    ],
    'js': [],
    'qweb': [],
    'installable': True,
    'application': True,
}
