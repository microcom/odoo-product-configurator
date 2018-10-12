# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_product_domain(self):
        if literal_eval(self.env['ir.config_parameter'].sudo().get_param('product_configurator.product_reusable', default='False')):
            return []
        else:
            return [('config_ok', '=', False)]

    product_id = fields.Many2one(domain=_get_product_domain)
