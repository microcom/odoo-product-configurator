# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductConfigurator(models.TransientModel):
    _inherit = 'product.configurator'

    purchase_order_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        readonly=True,
    )

    @api.multi
    def action_config_done(self):
        """ rebuilt from original """
        if self.env.context.get('active_model') == 'purchase.order':
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

            po = self.env['purchase.order'].browse(self.env.context.get('active_id'))

            line_vals = {'product_id': variant.id}
            # SO is not used, passing None
            line_vals.update(self._extra_line_values(None, variant, new=True))

            if self.purchase_order_line_id:
                self.purchase_order_line_id.write(line_vals)
            else:
                line_vals.update({
                    # taken from PurchaseOrderLine.onchange_product_id()
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_uom': variant.uom_po_id.id or variant.uom_id.id,
                    'price_unit': variant.standard_price,
                    'product_qty': 1
                })
                po.write({'order_line': [(0, 0, line_vals)]})

            self.unlink()
            return
        else:
            return super(ProductConfigurator, self).action_config_done()
