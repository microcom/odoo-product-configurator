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
    def action_config_done_postprocess(self, variant):
        if self.env.context.get('active_model') in ('purchase.order', 'purchase.order.line'):
            line_vals = {'product_id': variant.id}

            if self.purchase_order_line_id:
                # _extra_line_values() expects an SO but passing a PO also works
                line_vals.update(self._extra_line_values(self.purchase_order_line_id.order_id, variant, new=True))
                self.purchase_order_line_id.write(line_vals)
            else:
                po = self.env['purchase.order'].browse(self.env.context.get('active_id'))
                line_vals.update(self._extra_line_values(po, variant, new=True))
                # Changes start
                # Copied from sale.py - def create() to run onchange explicitly
                onchange_fields = ['name', 'price_unit', 'product_qty', 'taxes_id', 'product_uom', 'date_planned']
                line_vals['order_id'] = po.id
                if po.date_planned:
                    line_vals['date_planned'] = po.date_planned
                else:
                    line_vals['date_planned'] = fields.datetime.now()
                line = self.env['purchase.order.line'].new(line_vals)
                line.onchange_product_id()
                for field in onchange_fields:
                    if field not in line_vals:
                        line_vals[field] = line._fields[field].convert_to_write(line[field], line)
                # Changes ends
                po.write({'order_line': [(0, 0, line_vals)]})
        else:
            return super(ProductConfigurator, self).action_config_done_postprocess(variant)
