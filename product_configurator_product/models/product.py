# -*- coding: utf-8 -*-

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def reconfigure_product_variant(self):
        """ Copied from product_configurator_wizard.sale.py """

        cfg_steps = self.product_tmpl_id.config_step_line_ids
        active_step = str(cfg_steps[0].id) if cfg_steps else 'configure'
        last_step = str(cfg_steps[-1].id) if cfg_steps else 'configure'

        wizard_obj = self.env['product.configurator']
        wizard = wizard_obj.create({
            'modify_variant': True,
            'product_tmpl_id': self.id,
            'product_id': self.id,
            'state': active_step,
            'last_step': last_step,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator',
            'name': "Configure Product",
            'view_mode': 'form',
            'context': dict(
                self.env.context,
                wizard_id=wizard.id,
            ),
            'target': 'new',
            'res_id': wizard.id,
        }


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def reconfigure_product_template(self):
        """ Copied from product_configurator_wizard.sale.py """

        cfg_steps = self.config_step_line_ids
        active_step = str(cfg_steps[0].id) if cfg_steps else 'configure'
        last_step = str(cfg_steps[-1].id) if cfg_steps else 'configure'

        wizard_obj = self.env['product.configurator']
        wizard = wizard_obj.create({
            'modify_variant': False,
            'product_tmpl_id': self.id,
            'state': active_step,
            'last_step': last_step,
        })
        # Had to remove default_type because while creating mrp.bom it was taking type from product.template context
        ctx_no_type = self._context.copy()
        ctx_no_type.pop('default_type', None)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.configurator',
            'name': "Configure Product",
            'view_mode': 'form',
            'context': dict(
                ctx_no_type,
                wizard_id=wizard.id,
            ),
            'target': 'new',
            'res_id': wizard.id,
        }
