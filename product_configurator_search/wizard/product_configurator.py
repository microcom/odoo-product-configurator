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

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.product_tmpl_id = record.product_id.product_tmpl_id

    @api.multi
    @api.onchange('search_filter')
    def _onchange_search_filter(self):
        if self.search_filter:
            found = self.env['product.product'].search([('default_code', 'like', self.search_filter)])
            if found:
                self.product_id = found[0]
            return {'domain': {'product_id': [('default_code', 'like', self.search_filter)]}}
        else:
            return {'domain': {'product_id': []}}
