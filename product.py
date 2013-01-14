##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Andy Lu (<csnlca@gmail.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import netsvc
import pooler
from tools.translate import _
import decimal_precision as dp
from osv.orm import browse_record, browse_null
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'ext_id': fields.integer('Website Product'),
    }
    def init(self, cr):
        cr.execute('''update res_currency set active = false where name not in ('EUR','USD') and company_id = 1 ''')

product_product()

class res_partner(osv.osv):
    _inherit = "res.partner"

    _columns = {
        'ext_id': fields.integer('Website Product'),
    }

res_partner()

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'move_id': False,
            'purchase_id': False,
        })
        return super(procurement_order, self).copy(cr, uid, id, default, context=context)

    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from procurement
        @return: New created Purchase Orders procurement wise
        """
        res = {}
        if context is None:
            context = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        partner_obj = self.pool.get('res.partner')
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        prod_obj = self.pool.get('product.product')
        acc_pos_obj = self.pool.get('account.fiscal.position')
        seq_obj = self.pool.get('ir.sequence')
        warehouse_obj = self.pool.get('stock.warehouse')
        for procurement in self.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            partner = procurement.product_id.seller_id # Taken Main Supplier of Product of Procurement.
            seller_qty = procurement.product_id.seller_qty
            partner_id = partner.id
            address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            #Andy modify
            wh_id = procurement.warehouse_id
            if not wh_id:
                warehouse_ids = warehouse_obj.search(cr, uid, [('lot_stock_id', '=', procurement.location_id.id)], context=context)
                if not warehouse_ids:
                    warehouse_ids = warehouse_obj.search(cr, uid, [('company_id', '=', procurement.company_id.id or company.id)], context=context)
                wh_id = warehouse_ids and warehouse_obj.browse(cr, uid, warehouse_ids, context=context)[0] or False
            #Andy modify
            uom_id = procurement.product_id.uom_po_id.id

            qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
            if seller_qty:
                qty = max(qty,seller_qty)

            price = pricelist_obj.price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, partner_id, {'uom': uom_id})[pricelist_id]

            schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
            purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context)

            #Passing partner_id to context for purchase order line integrity of Line name
            context.update({'lang': partner.lang, 'partner_id': partner_id})

            product = prod_obj.browse(cr, uid, procurement.product_id.id, context=context)
            taxes_ids = procurement.product_id.product_tmpl_id.supplier_taxes_id
            taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)

            line_vals = {
                'name': product.partner_ref,
                'product_qty': qty,
                'product_id': procurement.product_id.id,
                'product_uom': uom_id,
                'price_unit': price or 0.0,
                'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'move_dest_id': res_id,
                'notes': product.description_purchase,
                'taxes_id': [(6,0,taxes)],
            }
 
            name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
            po_vals = {
                'name': name,
                'origin': procurement.origin,
                'partner_id': partner_id,
                'partner_address_id': address_id,
                #Andy modify
                'location_id': wh_id and wh_id.lot_input_id.id or procurement.location_id.id,
                'warehouse_id': wh_id and wh_id.id or False,
                #Andy modify end
                'pricelist_id': pricelist_id,
                'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': procurement.company_id.id,
                'fiscal_position': partner.property_account_position and partner.property_account_position.id or False
            }
            res[procurement.id] = self.create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=context)
            self.write(cr, uid, [procurement.id], {'state': 'running', 'purchase_id': res[procurement.id],'warehouse_id': wh_id and wh_id.id or False})
        return res

procurement_order()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        vals = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context)
        vals['warehouse_id'] = order.shop_id.warehouse_id.id
        return vals
sale_order()


class make_procurement(osv.osv_memory):
    _inherit = 'make.procurement'

    def make_procurement(self, cr, uid, ids, context=None):
        """ Creates procurement order for selected product.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary which loads Procurement form view.
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context).login
        wh_obj = self.pool.get('stock.warehouse')
        procurement_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        data_obj = self.pool.get('ir.model.data')

        for proc in self.browse(cr, uid, ids, context=context):
            wh = wh_obj.browse(cr, uid, proc.warehouse_id.id, context=context)
            procure_id = procurement_obj.create(cr, uid, {
                'name':'INT: '+str(user),
                'date_planned': proc.date_planned,
                'product_id': proc.product_id.id,
                'product_qty': proc.qty,
                'product_uom': proc.uom_id.id,
                'location_id': wh.lot_stock_id.id,
                'warehouse_id': wh.id, #Andy Add
                'procure_method':'make_to_order',
            })

            wf_service.trg_validate(uid, 'procurement.order', procure_id, 'button_confirm', cr)


        id2 = data_obj._get_id(cr, uid, 'procurement', 'procurement_tree_view')
        id3 = data_obj._get_id(cr, uid, 'procurement', 'procurement_form_view')

        if id2:
            id2 = data_obj.browse(cr, uid, id2, context=context).res_id
        if id3:
            id3 = data_obj.browse(cr, uid, id3, context=context).res_id

        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'res_id' : procure_id,
            'views': [(id3,'form'),(id2,'tree')],
            'type': 'ir.actions.act_window',
         }    
make_procurement()    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
