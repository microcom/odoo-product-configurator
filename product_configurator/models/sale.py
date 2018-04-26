# -*- coding: utf-8 -*-

from ast import literal_eval
from odoo import models, fields


# class sale_order_line_attribute(models.Model):
#     _name = 'sale.order.line.attribute'

#     custom_value = fields.Char('Custom Value', size=64)
#     sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_product_domain(self):
        if literal_eval(self.env['ir.config_parameter'].sudo().get_param('product_configurator.product_selectable', default='False')):
            return []
        else:
            return [('config_ok', '=', False)]

    custom_value_ids = fields.One2many(
        comodel_name='product.attribute.value.custom',
        inverse_name='product_id',
        related="product_id.value_custom_ids",
        string="Custom Values"
    )

    product_id = fields.Many2one(domain=_get_product_domain)
