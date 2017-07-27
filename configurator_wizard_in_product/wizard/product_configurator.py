# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from datetime import datetime


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
            if self.env.context.get('active_model') == 'product.template':
                steps = open_steps if (wiz.product_id or wiz.product_tmpl_id) else steps + open_steps
            else:
                steps = open_steps if wiz.product_id else steps + open_steps
        else:
            if self.env.context.get('active_model') == 'product.template':
                steps = [('configure', 'Configure')]
            else:
                steps.append(('configure', 'Configure'))
        return steps

    @api.multi
    def action_config_done(self):
        """This function is copied from product_configurator_wizard.ProductConfigurator
           added this function to check active_model=='product.template' to ignore running not necessary code"""
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
        domain = [['product_tmpl_id', '=', self.product_tmpl_id.id]]

        template_products = self.env['product.product'].search(domain)
        product_found = False

        if self.product_tmpl_id.reuse_variant:
            for product in template_products:
                if product.attribute_value_ids == self.value_ids:
                    product_found = product
                    break

        if product_found:
            variant = product_found
            price = product_found.standard_price
            uom = product_found.uom_id.id
        else:
            try:
                variant = self.product_tmpl_id.create_variant(
                    self.value_ids.ids, custom_vals)
                price = self.product_tmpl_id.standard_price
                uom = self.product_tmpl_id.uom_id.id
            except ValidationError:
                raise
            except:
                raise ValidationError(
                    _('Invalid configuration! Please check all '
                      'required steps and fields.')
                )

        if self.env.context.get('active_model') == 'purchase.order':
            order = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            line_vals = {'product_id': variant.id, 'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                         'product_uom': uom, 'price_unit': price, 'product_qty': 1}
        # Changes start
        elif self.env.context.get('active_model') == 'product.template':
            self.unlink()
            return
        # Changes end
        else:
            order = self.env['sale.order'].browse(self.env.context.get('active_id'))
            line_vals = {'product_id': variant.id}

        line_vals.update(self._extra_line_values(
            self.order_line_id.order_id or order, variant, new=True)
        )

        if self.order_line_id:
            self.order_line_id.write(line_vals)
        else:
            order.write({'order_line': [(0, 0, line_vals)]})

        self.unlink()
        return
