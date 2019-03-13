# -*- coding: utf-8 -*-

from ast import literal_eval
from lxml import etree

from odoo.osv import orm
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    product_id = fields.Many2one(readonly=False)
    search_filter = fields.Char('MPN')
    manufacturer_id = fields.Many2one(
        'product.attribute.value', string='Manufacturer', domain=lambda self: [
            ('attribute_id', '=', self.env.ref('product_configurator_search.attribute_manufacturer').id)])
    allowed_product_ids = fields.Many2many(
        'product.product', string='Allowed Products', compute='_compute_allowed_product_ids')

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        attribute_manufacturer = self.env.ref('product_configurator_search.attribute_manufacturer')
        for record in self:
            if record.product_id:
                record.product_tmpl_id = record.product_id.product_tmpl_id
                manufacturer_id = record.product_id.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == attribute_manufacturer)
                record.manufacturer_id = manufacturer_id

    @api.multi
    @api.onchange('search_filter')
    def _onchange_search_filter(self):
        self.ensure_one()
        # allowed_product_ids updated by search_filter
        if self.search_filter:
            self.product_id = self.allowed_product_ids and self.allowed_product_ids[0] or False
            return {'domain': {'product_id': [('id', 'in', self.allowed_product_ids.ids)]}}
        else:
            return {'domain': {'product_id': [('config_ok', '=', True)]}}

    @api.multi
    @api.depends('search_filter')
    def _compute_allowed_product_ids(self):
        self.ensure_one()
        attribute_mpn = self.env.ref('product_configurator_search.attribute_mpn')
        matching_values = self.env['product.attribute.value'].search([
            ('attribute_id', '=', attribute_mpn.id),
            ('name', 'like', self.search_filter),
        ])
        self.allowed_product_ids = matching_values.mapped('product_ids').filtered('config_ok')
