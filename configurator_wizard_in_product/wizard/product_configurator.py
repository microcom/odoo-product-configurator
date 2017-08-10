# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    @api.multi
    def get_state_selection(self):
        """ copied from product_configurator_wizard.product_configurator.py
            to add condition  to modify states if wizard is called
            from product.template object """

        steps = [('select', "Select Template")]

        # Get the wizard id from context set via action_next_step method
        wizard_id = self.env.context.get('wizard_id')

        if not wizard_id:
            return steps

        wiz = self.browse(wizard_id)

        open_lines = wiz.product_tmpl_id.get_open_step_lines(
            wiz.value_ids.ids)

        if open_lines:
            open_steps = open_lines.mapped(
                lambda x: (str(x.id), x.config_step_id.name)
            )
            if self.env.context.get('active_model') in ('product.template', 'product.product'):
                steps = open_steps if (wiz.product_id or wiz.product_tmpl_id) else steps + open_steps
            else:
                steps = open_steps if wiz.product_id else steps + open_steps
        else:
            if self.env.context.get('active_model') in ('product.template', 'product.product'):
                steps = [('configure', 'Configure')]
            else:
                steps.append(('configure', 'Configure'))
        return steps

    @api.multi
    def action_config_done(self):
        """ rebuilt from original """
        if self.env.context.get('active_model') in ('product.template', 'product.product'):
            custom_values = {
                l.attribute_id.id:
                    l.value or l.attachment_ids for l in self.custom_value_ids
            }
            duplicates = self.product_tmpl_id.search_variant(
                self.value_ids.ids, custom_values=custom_values)
            if duplicates:
                raise ValidationError(
                    _('Duplicate configuration! This variant already exists.')
                )

            # This try except is too generic.
            # The create_variant routine could effectively fail for
            # a large number of reasons, including bad programming.
            # It should be refactored.
            # In the meantime, at least make sure that a validation
            # error legitimately raised in a nested routine
            # is passed through.
            try:
                if self.product_id:
                    # extracted from create_get_variant
                    value_ids = self.value_ids.ids
                    valid = self.product_tmpl_id.validate_configuration(value_ids, custom_values)
                    if not valid:
                        raise ValidationError(_('Invalid Configuration'))
                    vals = self.product_tmpl_id.get_variant_vals(value_ids, custom_values)
                    self.product_id.write(vals)
                else:
                    self.product_tmpl_id.create_get_variant(
                        self.value_ids.ids, custom_values)
            except ValidationError:
                raise
            except:
                raise ValidationError(
                    _('Invalid configuration! Please check all '
                      'required steps and fields.')
                )

            self.unlink()
            return
        else:
            return super(ProductConfigurator, self).action_config_done()
