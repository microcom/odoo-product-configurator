# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_selectable = fields.Boolean('Product selectable')
    module_product_configurator_wizard = fields.Boolean('Configurator in sales')
    module_product_configurator_purchase = fields.Boolean('Configurator in purchase')
    module_product_configurator_product = fields.Boolean('Configurator in products')
    module_product_configurator_name = fields.Boolean('Configurator name')
    module_product_configurator_step_restriction = fields.Boolean('Configurator step restriction')
    module_product_configurator_use_default_pricelist = fields.Boolean('Configurator default price list')
    module_on_the_fly_default = fields.Boolean('Configurator create on the fly by default')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()

        product_selectable = literal_eval(params.get_param('product_configurator.product_selectable', default='False'))

        res.update(
            product_selectable=product_selectable
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param('product_configurator.product_selectable', self.product_selectable)

