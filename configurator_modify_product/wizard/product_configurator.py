# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    @api.multi
    def action_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        if not self.product_id:
            super(ProductConfigurator, self).action_config_done()
            return

        custom_vals = {
            l.attribute_id.id:
                l.value or l.attachment_ids for l in self.custom_value_ids
        }

        # This try except is too generic.
        # The create_variant routine could effectively fail for
        # a large number of reasons, including bad programming.
        # It should be refactored.
        # In the meantime, at least make sure that a validation
        # error legitimately raised in a nested routine
        # is passed through.
        try:
            variant = self.product_id
            duplicates = self.product_tmpl_id.find_duplicates(self.value_ids.ids, custom_vals)
            if not duplicates:
                # no other product match the variant, update it
                variant.update_variant(self.value_ids.ids, custom_vals)
            if variant in duplicates:
                # no change, leave as is
                pass
            else:
                # variant duplicates another product, warn user
                raise ValidationError(
                    _('Duplicate configuration! Variant already exists (id={})').format(duplicates[0].id)
                )


        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                _('Invalid configuration! Please check all '
                  'required steps and fields.')
            )

        self.action_config_done_postprocess(variant)
        self.unlink()
