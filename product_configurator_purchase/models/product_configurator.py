# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    purchase_order_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        readonly=True,
    )

    @api.multi
    def action_config_done(self):
        """ rebuilt from original """
        if self.env.context.get('active_model') in ('purchase.order', 'purchase.order.line'):
            # same behavior as sale.order
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
                variant = self.product_tmpl_id.create_get_variant(
                    self.value_ids.ids, custom_vals)
            except ValidationError:
                raise
            except:
                raise ValidationError(
                    _('Invalid configuration! Please check all '
                      'required steps and fields.')
                )
            line_vals = {'product_id': variant.id}

            if self.purchase_order_line_id:
                line_vals.update(self._extra_line_values(self.purchase_order_line_id.order_id, variant, new=True))
                self.purchase_order_line_id.write(line_vals)
            else:
                # Instead of passing None as a first argument now changed to po
                po = self.env['purchase.order'].browse(self.env.context.get('active_id'))
                line_vals.update(self._extra_line_values(po, variant, new=True))
                # Changes start
                # Copied from sale.py - def create() to run onchange explicitly
                onchange_fields = ['name', 'default_code', 'vendor_default_code', 'vendor_default_code_display',
                                   'price_unit', 'product_qty', 'taxes_id', 'product_uom', 'date_planned']
                line_vals['order_id'] = po.id
                line = self.env['purchase.order.line'].new(line_vals)
                line.onchange_product_id()
                for field in onchange_fields:
                    if field not in line_vals:
                        line_vals[field] = line._fields[field].convert_to_write(line[field], line)
                # Changes ends
                po.write({'order_line': [(0, 0, line_vals)]})

            self.unlink()
            return
        else:
            return super(ProductConfigurator, self).action_config_done()
