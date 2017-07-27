{
    'name': 'Configurator wizard from product',
    'category': 'Product',
    'summary': 'This module allows to modify variants and templates with the help of configurator wizard',
    'website': 'http://www.microcom.ca',
    'version': '10.0',
    'description': """
This module allows to modify variants and templates with the help of configurator wizard.
===================================================

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
