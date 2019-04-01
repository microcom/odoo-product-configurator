# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv.expression import FALSE_DOMAIN

# logic
# - always able to create a 2nd product with same part number but different manufacturer
# -- list all manufacturers
# -- list all templates
# template selected
# -- variant domain limited
# variant selected
# -- select part number + manufacturer + template
# part number typed
# -- variant domain limited (exact match)
# -- select variant if unique, cascade-select other fields
# manufacturer selected
# -- variant domain limited
# -- select variant if unique, cascade-select other fields
#

class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    product_id = fields.Many2one(readonly=False)
    search_filter = fields.Char('MPN')
    mpn_ids = fields.Many2many(
        'product.attribute.value', string='Manufacturer', domain=lambda self: [
            ('attribute_id', '=', self.env.ref('product_configurator_search.attribute_mpn').id)])
    manufacturer_id = fields.Many2one(
        'product.attribute.value', string='Manufacturer', domain=lambda self: [
            ('attribute_id', '=', self.env.ref('product_configurator_search.attribute_manufacturer').id)])

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.ensure_one()
        if self.product_id:
            self.product_tmpl_id = self.product_id.product_tmpl_id
            # set mpn
            attribute_mpn = self.env.ref('product_configurator_search.attribute_mpn')
            mpn_id = self.product_id.attribute_value_ids.filtered(
                lambda x: x.attribute_id == attribute_mpn)
            if mpn_id:
                self.search_filter = mpn_id.name
            else:
                self.search_filter = ''
            # set manufacturer
            attribute_manufacturer = self.env.ref('product_configurator_search.attribute_manufacturer')
            self.manufacturer_id = self.product_id.attribute_value_ids.filtered(
                lambda x: x.attribute_id == attribute_manufacturer)

    @api.multi
    @api.onchange('search_filter')
    def _onchange_search_filter(self):
        if self.search_filter and len(self.search_filter) > 2:
            attribute_mpn = self.env.ref('product_configurator_search.attribute_mpn')
            self.mpn_ids = self.env['product.attribute.value'].search([
                ('attribute_id', '=', attribute_mpn.id),
                ('name', '=', self.search_filter),
            ])
        else:
            self.mpn_ids = None
        return self.update_variant_domain(select=True)

    @api.multi
    @api.onchange('manufacturer_id')
    def _onchange_manufacturer_id(self):
        return self.update_variant_domain(select=False)

    @api.multi
    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        return self.update_variant_domain(select=False)

    @api.multi
    def update_variant_domain(self, select=True):
        self.ensure_one()
        if self.env.context.get('noupdate_variant', False):
            return
        # dataset might be emptied when combining domains, test against explicit None to differentiate
        allowed_product_ids = None
        if self.search_filter and len(self.search_filter) > 2:
            allowed_product_ids = self.mpn_ids.mapped('product_ids').filtered('config_ok')
        if self.manufacturer_id:
            manufacturer_products = self.manufacturer_id.mapped('product_ids').filtered('config_ok')
            if allowed_product_ids is None:
                allowed_product_ids = manufacturer_products
            else:
                allowed_product_ids &= manufacturer_products
        if self.product_tmpl_id:
            if allowed_product_ids is None:
                allowed_product_ids = self.env['product.product'].search(
                    [('product_tmpl_id', '=', self.product_tmpl_id.id)])
            else:
                allowed_product_ids = allowed_product_ids.filtered(
                    lambda x: x.product_tmpl_id == self.product_tmpl_id)
        # no filter
        if allowed_product_ids is None:
            return {'domain': {'product_id': [('config_ok', '=', True)]}}
        # clear on empty domain
        if len(allowed_product_ids) == 0:
            self.product_id = None
            return {'domain': {'product_id': FALSE_DOMAIN}}
        # assign unique
        if len(allowed_product_ids) == 1 and select:
            self.with_context(noupdate_variant=True).product_id = allowed_product_ids[0]
        return {'domain': {'product_id': [('id', 'in', allowed_product_ids.ids)]}}
