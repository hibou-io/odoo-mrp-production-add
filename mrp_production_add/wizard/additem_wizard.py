# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math


class AddProductionItem(models.TransientModel):
    _name = 'wiz.add.production.item'
    _description = 'Add Production Item'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float(
        'Product Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True,
        default=1.0)
    production_id = fields.Many2one(
        'mrp.production', 'Production Order', select=True,
        default=lambda self: self.env.context.get('active_id', False))

    @api.multi
    def add_item(self):
        for item in self:
            if item.product_qty <= 0:
                raise UserError('Please provide a positive quantity to add')

            bom_line = self.env['mrp.bom.line'].create({
                'product_id': item.product_id.id,
                'product_qty': item.product_qty,
                'bom_id': item.production_id.bom_id.id
            })

            move = item.production_id._generate_raw_move(bom_line, {'qty': item.product_qty, 'parent_line': None})
            item.production_id._adjust_procure_method()
            move.action_confirm()
            bom_line.unlink()

        return True
