# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_reusable = fields.Boolean('Product reusable')
    product_modifiable = fields.Boolean('Product modifiable')
    module_product_configurator_wizard = fields.Boolean('Configurator in sales')
    module_product_configurator_purchase = fields.Boolean('Configurator in purchase')
    module_product_configurator_product = fields.Boolean('Configurator in products')
    module_product_configurator_name = fields.Boolean('Configurator name')
    module_product_configurator_search = fields.Boolean('Configurator MPN Search')
    product_name_separator = fields.Char('Name separator')
    module_product_configurator_step_restriction = fields.Boolean('Configurator step restriction')
    module_product_configurator_use_default_pricelist = fields.Boolean('Configurator default price list')
    module_on_the_fly_default = fields.Boolean('Configurator create on the fly by default')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()

        product_reusable = literal_eval(params.get_param('product_configurator.product_reusable', default='False'))
        product_modifiable = literal_eval(params.get_param('product_configurator.product_modifiable', default='False'))
        product_name_separator = params.get_param('product_configurator_name.product_name_separator')

        res.update(
            product_reusable=product_reusable,
            product_modifiable=product_modifiable,
            product_name_separator=product_name_separator
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param('product_configurator.product_reusable', self.product_reusable)
        self.env['ir.config_parameter'].sudo().set_param('product_configurator.product_modifiable', self.product_modifiable)
        self.env['ir.config_parameter'].sudo().set_param('product_configurator_name.product_name_separator', self.product_name_separator)

    @api.onchange('product_reusable')
    def _onchange_product_reusable(self):
        for record in self:
            # cannot have both False, reactivate the other
            if not (record.product_reusable or record.product_modifiable):
                record.product_modifiable = True

    @api.onchange('product_modifiable')
    def _onchange_product_modifiable(self):
        for record in self:
            # cannot have both False, reactivate the other
            if not (record.product_reusable or record.product_modifiable):
                record.product_reusable = True
