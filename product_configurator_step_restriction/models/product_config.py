# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductConfigRestriction(models.Model):
    """This class is a clone of ProductConfigDomain"""
    _name = 'product.config.restriction'

    @api.multi
    @api.depends('implied_ids')
    def _get_trans_implied(self):
        "Computes the transitive closure of relation implied_ids"

        def linearize(domains):
            trans_domains = domains
            for domain in domains:
                implied_domains = domain.implied_ids - domain
                if implied_domains:
                    trans_domains |= linearize(implied_domains)
            return trans_domains

        for domain in self:
            domain.trans_implied_ids = linearize(domain)

    @api.multi
    def compute_domain(self):
        """ Returns a list of domains defined on a product.config.domain_line_ids
            and all implied_ids"""
        # TODO: Enable the usage of OR operators between implied_ids
        # TODO: Add implied_ids sequence field to enforce order of operations
        # TODO: Prevent circular dependencies
        computed_domain = []
        for domain in self:
            lines = domain.trans_implied_ids.mapped('domain_line_ids').sorted()
            for line in lines[:-1]:
                if line.operator == 'or':
                    computed_domain.append('|')
                computed_domain.append(
                    (line.attribute_id.id,
                     line.condition,
                     line.value_ids.ids)
                )
            # ensure 2 operands follow the last operator
            computed_domain.append(
                (lines[-1].attribute_id.id,
                 lines[-1].condition,
                 lines[-1].value_ids.ids)
            )
        return computed_domain

    name = fields.Char(
        string='Name',
        required=True,
        size=256
    )
    domain_line_ids = fields.One2many(
        comodel_name='product.config.restriction.line',
        inverse_name='domain_id',
        string='Restrictions',
        required=True
    )
    implied_ids = fields.Many2many(
        comodel_name='product.config.restriction',
        relation='product_config_restriction_implied_rel',
        string='Inherited',
        column1='domain_id',
        column2='parent_id'
    )
    trans_implied_ids = fields.Many2many(
        comodel_name='product.config.restriction',
        compute=_get_trans_implied,
        column1='domain_id',
        column2='parent_id',
        string='Transitively inherits'
    )


class ProductConfigRestrictionLine(models.Model):
    """This class is a clone of ProductConfigDomainLine"""
    _name = 'product.config.restriction.line'
    _order = 'sequence'

    def _get_domain_conditions(self):
        operators = [
            ('in', 'In'),
            ('not in', 'Not In')
        ]

        return operators

    def _get_domain_operators(self):
        andor = [
            ('and', 'And'),
            ('or', 'Or'),
        ]

        return andor

    attribute_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Attribute',
        required=True)

    domain_id = fields.Many2one(
        comodel_name='product.config.restriction',
        required=True,
        string='Rule')

    condition = fields.Selection(
        selection=_get_domain_conditions,
        string="Condition",
        required=True)

    value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='product_config_restriction_line_attr_rel',
        column1='line_id',
        column2='attribute_id',
        string='Values',
        required=True
    )

    operator = fields.Selection(
        selection=_get_domain_operators,
        string='Operators',
        default='and',
        required=True
    )

    sequence = fields.Integer(
        string="Sequence",
        default=1,
        help="Set the order of operations for evaluation domain lines"
    )


class ProductConfigStepLine(models.Model):
    _inherit = 'product.config.step.line'

    restriction_id = fields.Many2one(
        comodel_name='product.config.restriction',
        string='Restriction',
        required=True
        )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
        if not open_step_lines:
            open_step_lines = self.get_open_step_lines(value_ids, force_all=True)
        return open_step_lines.sorted()
