# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    name_override = fields.Char('Custom Name')
    hidden_attribute_value_ids = fields.Many2many('product.attribute.value', string='Hidden Attributes', compute='_compute_hidden')
    attribute_description = fields.Html('Attributes Description', compute='_compute_attribute_description')

    def _compute_hidden(self):
        for product in self:
            hidden_ids = self.env['product.attribute.value']
            for line in product.attribute_line_ids.sorted('sequence'):
                if line.display_mode == 'hide':
                    key = line.attribute_id.name
                    for value in product.attribute_value_ids:
                        if value.attribute_id.name == key:
                            hidden_ids += value
            product.hidden_attribute_value_ids = hidden_ids

    def _compute_attribute_description(self):
        separator = '%s ' % self.env['ir.config_parameter'].sudo().get_param('product_configurator_name.product_name_separator', default="''")
        for product in self:
            # prefetch values
            value_dict = {}
            for value in product.attribute_value_ids:
                old_value = value_dict.get(value.attribute_id.name)
                if old_value:
                    value_dict[value.attribute_id.name] = separator.join([old_value, value.name])
                else:
                    value_dict[value.attribute_id.name] = value.name
            # assemble variant
            novalue = _('<span style="color: #a8a8a8;">None</span>')  # @odoo-main-color-muted: #a8a8a8;
            name_elements = []
            for line in product.attribute_line_ids.sorted('sequence'):
                key = line.attribute_id.name
                value = value_dict.get(key, novalue)
                name_elements.append(u'<li><strong>{}:</strong> {}</li>'.format(key, value))
            product.attribute_description = u'<ul>{}</ul>'.format(u''.join(name_elements))

    def get_attribute_array(self):
        # prefetch values
        value_dict = defaultdict(list)
        for value in self.attribute_value_ids:
            value_dict[value.attribute_id.name].append(value.name)
        for value in self.value_custom_ids:
            value_dict[value.attribute_id.name].append(value.name)
        # match lines
        return [
            (line.attribute_id, line.display_mode, value_dict[line.attribute_id.name])
            for line in self.attribute_line_ids.sorted('sequence')]

    @api.multi
    def name_get(self):
        """ Override variant name
        """
        def _name_get(d):
            name = d.get('name', '')
            supplier_code = self._context.get('display_default_code', True) and d.get('supplier_code', False) or False
            default_code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if supplier_code:
                name = '[%s] %s' % (supplier_code, name)
            if default_code:
                name = '[%s] %s' % (default_code, name)
            return (d['id'], name)

        separator = '%s ' % self.env['ir.config_parameter'].sudo().get_param('product_configurator_name.product_name_separator', default="''")

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []
        for product in self.sudo():
            # START CHANGES
            if product.name_override:
                name = product.name_override
            else:
                if product.config_ok:
                    name_elements = []
                    for line, mode, value in product.get_attribute_array():
                        if mode == 'hide' or not len(value):
                            continue
                        if mode == 'value':
                            name_elements.append(separator.join(value))
                        elif mode == 'attribute':
                            name_elements.append('{}: {}'.format(line.name, separator.join(value)))
                    variant = separator.join(name_elements)
                else:
                    # display only the attributes with multiple possible values on the template
                    variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
                    variant = product.attribute_value_ids._variant_name(variable_attributes)

                name = variant and "%s%s%s" % (product.name, separator, variant) or product.name
            # END CHANGES
            sellers = []
            if partner_ids:
                sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
                if not sellers:
                    sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
            # START CHANGES
            if len(sellers) > 0 and sellers[0].product_id and sellers[0].product_name:
                # variant supplierinfo name has priority
                temp = (product.id, sellers[0].product_name)
                if temp not in result:
                    result.append(temp)
                continue
            elif product.name_override:
                # variant name_override bypasses normal behavior
                temp = (product.id, product.name_override)
                if temp not in result:
                    result.append(temp)
                continue
            # resume normal behavior
            # template supplierinfo name will replace template name
            # prefixed with default_code and supplier_code
            # END CHANGES
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s%s%s" % (s.product_name, separator, variant) or s.product_name
                        ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': product.default_code or '',
                        'supplier_code': s.product_code or ''
                        }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                    }
                result.append(_name_get(mydict))
        return result
