# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductConfigStepLine(models.Model):
    _inherit = 'product.config.step.line'

    restriction_id = fields.Many2one(
        comodel_name='product.config.domain',
        string='Applied if'
        )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    """
    Copy this function from product_configurator\product_config.py. To skip some step in term of restriction.
    """
    def get_open_step_lines(self, value_ids, force_all=False):
        """
        Returns a recordset of configuration step lines open for access given
        the configuration passed through value_ids

        e.g: Field A and B from configuration step 2 depend on Field C
        from configuration step 1. Since fields A and B require action from
        the previous step, configuration step 2 is deemed closed and redirect
        is made for configuration step 1.

        :param value_ids: list of value.ids representing the
                          current configuration
        :returns: recordset of accesible configuration steps
        """

        open_step_lines = self.env['product.config.step.line']

        for cfg_line in self.config_step_line_ids:
            if not force_all:
                show_step = True
                for domain_line in cfg_line.restriction_id.domain_line_ids:
                    domain_value_ids = domain_line.value_ids
                    if domain_line.condition == 'in':
                        matching_ids = domain_value_ids.filtered(lambda x: x.id in value_ids)
                        if matching_ids and domain_line.operator == 'or':
                            break
                        if not matching_ids and domain_line.operator == 'and':
                            show_step = False
                            break
                    if domain_line.condition == 'not in':
                        matching_ids = domain_value_ids.filtered(lambda x: x.id in value_ids)
                        if not matching_ids and domain_line.operator == 'or':
                            break
                        if matching_ids and domain_line.operator == 'and':
                            show_step = False
                            break
                if not show_step:
                    continue
            for attr_line in cfg_line.attribute_line_ids:
                available_vals = self.values_available(attr_line.value_ids.ids,
                                                       value_ids)
                # TODO: Refactor when adding restriction to custom values
                if available_vals or attr_line.custom:
                    open_step_lines |= cfg_line
                    break
        if not open_step_lines and self.config_step_line_ids:
            open_step_lines = self.get_open_step_lines(value_ids, force_all=True)
        return open_step_lines.sorted()
