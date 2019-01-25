# -*- coding: utf-8 -*-

from ast import literal_eval
from lxml import etree

from odoo.osv import orm
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    product_id = fields.Many2one(readonly=False)
    search_filter = fields.Char('Search Code')
    allowed_product_ids = fields.Many2many(
        'product.product', string='Allowed Products', compute='_compute_allowed_product_ids')

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.product_tmpl_id = record.product_id.product_tmpl_id

    @api.multi
    @api.onchange('search_filter')
    def _onchange_search_filter(self):
        self.ensure_one()
        # allowed_product_ids updated by search_filter
        if self.allowed_product_ids:
            self.product_id = self.allowed_product_ids[0]
            return {'domain': {'product_id': [('id', 'in', self.allowed_product_ids.ids)]}}
        else:
            return {'domain': {'product_id': []}}

    @api.multi
    @api.depends('search_filter')
    def _compute_allowed_product_ids(self):
        self.ensure_one()
        attribute_mpn = self.env.ref('product_configurator_search.attribute_mpn')
        matching_values = self.env['product.attribute.value'].search([
            ('attribute_id', '=', attribute_mpn.id),
            ('name', 'like', self.search_filter),
        ])
        self.allowed_product_ids = matching_values.mapped('product_ids')
