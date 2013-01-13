# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

{
    'name': 'OG Init. Data',
    'version': '1.3',
    'category': 'Sales Management',
    "sequence": 14,
    'complexity': "easy",
    'description': """
The init. data module to manage shops and warehouses.
======================================================
        * Create company, currency, partner
        * Create location, warehouse
        * Create shop
        * Create test account
        * Add depend purchase module, setup purchase manager  v1.1
        * Add depend hr moudle, setup hr manager, erp manager v1.2
        * Add depend mrp moudle, setup mrp manager            v1.3
        * Add ext_id for product, partner
======================================================
    """,
    'author': 'Andy Lu',
    'website': 'http://weibo.com/210102899',
    'images': [],
    'depends': ['base', 'account', 'stock', 'purchase', 'sale', 'hr', 'mrp'],
    'init_xml': [],
    'update_xml': [
        'hkh-default_data.xml',
        'bv-update_data.xml',
        'cy-default_data.xml',
        'he-default_data.xml',

        'ca-britishcolumbia_data.xml',
        'us-washington_data.xml',
        'us-nevada_data.xml',
        'do-stdomingo_data.xml',
        'ec-guayas_data.xml',

        'jm-kingston_data.xml',
        'jm-motegobay_data.xml',
        'jm-ochorios_data.xml',
        'jm-manderville_data.xml',
        'mx-mexicocity_data.xml',
        'mx-chihuahua_data.xml',
        'mx-guadalajara_data.xml',

        'pe-lima_data.xml',
        'hki-default_data.xml',
        'hkm-default_data.xml',
        'tw-taipei_data.xml',
        'ph-quezoncity_data.xml',

        'jp-default_data.xml',
        'cl-default_data.xml',
        'br-default_data.xml',

        'my-petalingjaya_data.xml',
        'my-sabah_data.xml',
        'my-sarawak_data.xml',
        'ua-kiev_data.xml',
        'ru-moscow_data.xml',

        'he-nl_tilburg_data.xml',

        'product_view.xml',
    ],
    'demo_xml': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
