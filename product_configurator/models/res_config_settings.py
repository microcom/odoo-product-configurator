# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_selectable = fields.Boolean('Product selectable')

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

