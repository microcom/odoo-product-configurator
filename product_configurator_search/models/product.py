# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def find_duplicates(self, value_ids, custom_values=None, product_id=None):
        duplicates = super(ProductTemplate, self).find_duplicates(
            value_ids, custom_values=custom_values, product_id=product_id)
        if not duplicates:
            # test for partial match on manufacturer and mpn
            attribute_mpn = self.env.ref('product_configurator_search.attribute_mpn')
            attribute_manufacturer = self.env.ref('product_configurator_search.attribute_manufacturer')
            value_mpn = attribute_mpn.value_ids.filtered(lambda x: x.id in value_ids)
            value_manufacturer = attribute_manufacturer.value_ids.filtered(lambda x: x.id in value_ids)
            if value_mpn and value_manufacturer:
                # no duplicates means some attribute has changed,
                # check if mpn/manufacturer are same as before
                found = value_mpn.product_ids & value_manufacturer.product_ids
                if found and product_id != found:
                    raise ValidationError(_('Duplicate manufacturer product number'))
        return duplicates
