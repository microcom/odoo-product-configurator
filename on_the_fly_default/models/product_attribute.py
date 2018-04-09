# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    create_on_the_fly = fields.Boolean(default=True)