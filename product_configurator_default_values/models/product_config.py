# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductConfigLine(models.Model):
    _inherit = 'product.config.line'

    default_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        id1="cfg_line_id",
        id2="attr_val_id",
        string="Default"
    )
    immutable = fields.Boolean(string='Immutable')
