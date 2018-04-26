# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _rec_name = 'config_name'

    """
    Copy the function from product_configurator to show price using price list.
    To Fix :
        - Extra price For Attribute value
        - Extra price For Custom value.
    """
    @api.multi
    def _compute_product_price_extra(self):
        """Compute price of configurable products as sum
        of products related to attribute values picked"""
        products = self.filtered(lambda x: not x.config_ok)
        pricelist = self.env.user.partner_id.property_product_pricelist
        configurable_products = self - products
        if products:
            prices = super(ProductProduct, self)._compute_product_price_extra()

        conversions = self._get_conversions_dict()
        for product in configurable_products:
            lst_price = product.product_tmpl_id.lst_price
            value_ids = product.attribute_value_ids.ids
            # TODO: Merge custom values from products with cfg session
            # and use same method to retrieve parsed custom val dict
            custom_vals = {}
            for val in product.value_custom_ids:
                custom_type = val.attribute_id.custom_type
                if custom_type in conversions:
                    try:
                        custom_vals[val.attribute_id.id] = conversions[
                            custom_type](val.value)
                    except:
                        raise ValidationError(
                            _("Could not convert custom value '%s' to '%s' on "
                              "product variant: '%s'" % (val.value,
                                                         custom_type,
                                                         product.display_name))
                        )
                else:
                    custom_vals[val.attribute_id.id] = val.value
            #
            # prices = product.product_tmpl_id.get_cfg_price(
            #     value_ids, custom_vals)
            product_price = pricelist.get_product_price(product, 1, 1)
            # product.price_extra = prices['total'] - prices['taxes'] - lst_price
            product.price_extra = product_price - lst_price