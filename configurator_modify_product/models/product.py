# -*- coding: utf-8 -*-

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def find_duplicates(self, value_ids, custom_values=None):
        """
        Copy of create_get_variant(), returns without creating new variant
        """
        if custom_values is None:
            custom_values = {}
        valid = self.validate_configuration(value_ids, custom_values)
        if not valid:
            raise ValidationError(_('Invalid Configuration'))

        duplicates = self.search_variant(value_ids,
                                         custom_values=custom_values)

        # At the moment, I don't have enough confidence with my understanding
        # of binary attributes, so will leave these as not matching...
        # In theory, they should just work, if they are set to "non search"
        # in custom field def!
        # TODO: Check the logic with binary attributes
        if custom_values:
            value_custom_ids = self.encode_custom_values(custom_values)
            if any('attachment_ids' in cv[2] for cv in value_custom_ids):
                duplicates = False

        return duplicates


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def update_variant(self, value_ids, custom_values=None):
        self.ensure_one()
        # extracted from get_variant_vals()
        vals = {'attribute_value_ids': [(6, 0, value_ids)]}
        if custom_values:
            vals.update({
                'value_custom_ids': self.encode_custom_values(custom_values)
            })
        # write instead of create, from create_get_variant()
        self.write(vals)
        return self
