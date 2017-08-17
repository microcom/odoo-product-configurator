# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    @api.multi
    def get_state_selection(self):
        """ Select Template step is removed for product template/variant buttons """
        if self.env.context.get('active_model') in ('product.template', 'product.product'):
            # simplified from get_state_selection()

            # called through reconfigure_product_variant() or reconfigure_product_template()
            # wizard id is always in the context
            wizard_id = self.env.context.get('wizard_id')

            wiz = self.browse(wizard_id)
            open_lines = wiz.product_tmpl_id.get_open_step_lines(
                wiz.value_ids.ids)

            if open_lines:
                open_steps = open_lines.mapped(
                    lambda x: (str(x.id), x.config_step_id.name)
                )
                # CHANGE - ignore Select Template step
                steps = open_steps
            else:
                steps = [('configure', 'Configure')]
            return steps
        else:
            return super(ProductConfigurator, self).get_state_selection()

    @api.multi
    def action_config_done_postprocess(self, variant):
        if self.env.context.get('active_model') in ('product.template', 'product.product'):
            # nothing to do
            pass
        else:
            return super(ProductConfigurator, self).action_config_done_postprocess(variant)
