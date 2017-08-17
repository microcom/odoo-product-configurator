# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    modify_variant = fields.Boolean(string='Modify Variant')


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    modify_variant = fields.Boolean(
        related='company_id.modify_variant',
        string="Reconfigure button in sale order lines will modify variant for all orders.")
