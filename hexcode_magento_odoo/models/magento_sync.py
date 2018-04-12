# -*- coding: utf-8 -*-

import base64
import random
import threading
import xmlrpc.client

import requests
import string

from datetime import date
import logging
from odoo import fields,models,api, SUPERUSER_ID


#Importazione/Esportazione Dati
from odoo import sql_db
from odoo.api import Environment
from odoo.osv import osv

#pip install rauth
#from requests_oauthlib import OAuth1

#import sys
#reload(sys)
#sys.setdefaultencoding("utf8")







class magento_sync(models.Model):
    _name = 'magento.sync'

    store_ids = fields.Many2one('magento.store')




    def connection(self, website):
        if not website.url:
            raise osv.except_osv("Warning!", " Configure Magento Settings")
        else:
            url = website.url
            if not url.startswith('http') and not url.startswith('192'):
                url = 'https://' + website.url
            socket = xmlrpc.client.ServerProxy(url+"/index.php/api/xmlrpc")
            try:
                session = socket.login(website.username, website.password)
                return socket, session
            except:
                print('Errore Connessione a Magento')




    def getSettings(self):
        magento_settings = self.env['magento.settings'].search([])
        if not magento_settings:
            magento_settings = self.env['magento.settings'].create({})
        return magento_settings

    def random(self, length):
        return ''.join(random.choice(string.lowercase) for i in range(length))




    def export_stock(self):
        # Connect to WS Magento
        socket, session = self.connection()
        #Prendo tutti i prodotti magento
        product_ids = self.env['product.product'].search([('magento_id', '!=', False)])

        for product in product_ids:
            parameter = []
            datas = {}
            stock_data = {}
            product_uom_qty_ids = self.env['stock.quant'].search([('product_id', '=', int(product.id))])
            if product_uom_qty_ids:
                sum = 0
                for product_qty in product_uom_qty_ids:
                    sum += product_qty.qty
                stock_data['qty'] = str(sum)
            else:
                stock_data['qty'] = '0'
            datas['stock_data'] = stock_data

            parameter.append(str(product.magento_id))
            parameter.append(datas)
            parameter.append('1')
            parameter.append(self.random(10))
            id = socket.call(session, "catalog_product.update", parameter)



    def export_product(self):
        # Connect to WS Magento
        socket, session = self.connection()
        product_ids = self.env['product.product'].search([('magento_id', '=', False)])
        for product in product_ids:
            print(product.default_code)
            parameter = []
            vals = {}
            #Product Type
            parameter.append(str(product.magento_type.type))
            #Product Set
            parameter.append(str(product.magento_set.magento_id))
            #Product Sku
            if product.default_code:
                parameter.append(str(product.default_code))
            else:
                parameter.append(str(self.random(5)))
            # Valori Extra
            if product.magento_status:
                vals['status'] = str('1')
            else:
                vals['status'] = str('2')
            vals['visibility'] = str(product.magento_visibility)
            if product.magento_special_price:
                vals['special_price'] = product['magento_special_price']
            if product.magento_special_from_date:
                vals['special_from_date'] = str(product.magento_special_from_date)
            if product.magento_special_to_date:
                vals['special_to_date'] = str(product.magento_special_to_date)
            if product.magento_meta_title:
                vals['meta_title'] = str(product.magento_meta_title)
            if product.magento_meta_keyword:
                vals['meta_keyword'] = str(product.magento_meta_keyword)
            if product.magento_meta_description:
                vals['meta_description'] = str(product.magento_meta_description)
            if product.magento_custom_design:
                vals['custom_design'] = str(product.magento_custom_design)
            if product.name:
                vals['name'] = str(product.name)
            if product.list_price:
                vals['price'] = str(product.list_price)
            if product.description_sale:
                vals['description'] = str(product.description_sale)

            category_ids = []
            for category in product.magento_category_ids:
                if category.magento_id:
                    category_ids.append(str(category.magento_id))
            if len(category_ids) > 0:
                vals['category_ids'] = category_ids
            parameter.append(vals)
            #StoreView
            parameter.append('1')
            #Creo Il prodotto
            id = socket.call(session, "catalog_product.create", parameter)
            product.write({'magento_id': int(id)})


            #Ciclo tutte le foto e le aggiungo a media_list
            for file in product.magento_images_ids:
                # Carico Le foto
                media_param = []
                # Product ID
                media_param.append(str(product.magento_id))

                # Media List
                medias = {}

                # File List
                medias_list = {}
                #Base64
                medias_list['content'] = str(file.datas)
                medias_list['mime'] = str(file.mimetype)
                medias_list['name'] = str(file.name)

                medias['file'] = medias_list
                medias['label'] = str(file.description)
                medias['position'] = str(file.sortable)

                #Media
                media_param.append(medias)
                #StoreView
                media_param.append('1')
                media_param.append('slxxmckdoe')
                media_result = socket.call(session, "catalog_product_attribute_media.create", media_param)


    def export_sale_order_status(self):
        # Connect to WS Magento
        socket, session = self.connection()
        order_ids = self.env['sale.order'].search([('magento_id','!=', False)])
        for order in order_ids:
            sale_param = []
            #Order Increment
            sale_param.append(str(order.magento_id))
            if order.state == 'cancel':
                sale_param.append(str('canceled'))
            if order.state == 'sale':
                sale_param.append(str('complete'))
            if order.state == 'sent':
                sale_param.append(str('processing'))
            if order.state == 'draft':
                sale_param.append(str('pending'))
            if order.magento_comment:
                sale_param.append(str(order.magento_comment))
            socket.call(session, "sales_order.addComment", sale_param)


    def export_customer(self):
        # Connect to WS Magento
        socket, session = self.connection()
        customer_ids = self.env['res.partner'].search(['&',('magento_id', '=', False), ('customer', '=', True)])
        for customer in customer_ids:
            vals = {}
            if customer.email:
                vals['email'] = customer.email
            magento_settings = self.getSettings()
            if not customer.email and magento_settings.magento_customer_email:
                vals['email'] = magento_settings.magento_customer_email
            if not magento_settings.magento_customer_email and not customer.email:
                vals['email'] = 'demo@demo.com'
            if customer.name:
                vals['firstname'] = customer.name
            if customer.website_id:
                vals['website_id'] = str(customer.website_id)
            if customer.store_id:
                vals['store_id'] = str(customer.store_id.magento_id)
            if customer.mfirstname:
                vals['firstname'] = customer.mfirstname
            if customer.mlastname:
                vals['lastname'] = customer.mlastname
            if customer.mpassword:
                vals['password'] = customer.mpassword
            if customer.mgender:
                vals['gender'] = customer.mgender
            if customer.mmiddlename:
                vals['mmiddlename'] = customer.mmiddlename
            if customer.magento_group:
                vals['group_id'] = str(customer.magento_group.magento_group_id)

            try:
                id = socket.call(session, "customer.create", [vals])
                customer.write({'magento_id': int(id)})
            except Exception:
                print('s')

    def product_type_magento(self):
        # Connect to WS Magento
        settings = self.getSettings()
        for website in settings:
            socket, session = self.connection(website)
            types = socket.call(session, "catalog_product_type.list")
            for type in types:
                exist = self.env['magento.product.type'].search([('type', '=', type['type'])])
                vals = {}
                if 'type' in type:
                    vals['type'] = type['type']
                    vals['name'] = type['type']
                if 'label' in type:
                    vals['label'] = type['label']
                if not exist:
                    self.env['magento.product.type'].create(vals)
                else:
                    exist.write(vals)

    def store_magento(self):
        settings = self.getSettings()
        for website in settings:
            # Connect to WS Magento
            socket, session = self.connection(website)
            stores = socket.call(session, "store.list")
            for store in stores:
                exist = self.env['magento.store'].search([('magento_id','=',int(store['store_id']))])
                vals = {}
                if 'code' in store:
                    vals['code'] = store['code']
                if 'website_id' in store:
                    vals['website_id'] = store['website_id']
                if 'group_id' in store:
                    vals['group_id'] = store['group_id']
                if 'name' in store:
                    vals['name'] = store['name']
                if 'sort_order' in store:
                    vals['sort_order'] = store['sort_order']
                if 'is_active' in store:
                    vals['is_active'] = store['is_active']
                vals['magento_id'] = store['store_id']
                vals['store_id'] = store['store_id']

                if not exist:
                    self.env['magento.store'].create(vals)
                else:
                    exist.write(vals)

    def customer_group_magento(self):
        # Connect to WS Magento
        socket, session = self.connection()
        groups = socket.call(session, "customer_group.list")
        vals = {}
        for group in groups:
            exist = self.env['magento.customers.group'].search([('magento_group_id', '=', int(group['customer_group_id']))])
            if 'customer_group_id' in group:
                vals['magento_group_id'] = int(group['customer_group_id'])
            if 'customer_group_code' in group:
                vals['magento_group_code'] = group['customer_group_code']
                vals['name'] = group['customer_group_code']
            if not exist:
                self.env['magento.customers.group'].create(vals)
            else:
                exist.write(vals)

    def category_magento(self):
        # Connect to WS Magento
        #self.connection_rest()
        settings = self.getSettings()

        for website in settings:
            socket, session = self.connection(website)
            categories = socket.call(session, "catalog_category.tree", [])
            # Website
            web_site = self.env['multi.magento.website'].search([('name', '=', website.url)], limit=1)
            if not web_site:
                web_site = self.env['multi.magento.website'].create({'name': website.url, 'url': website.url})
            self.recursive_category(categories, web_site)

        return True


    def recursive_category(self, category, website):
        categories_obj = self.env['product.category']
        exist = categories_obj.search(['&', ('magento_website_id', '=', int(website.id)),('magento_id', '=', int(category['category_id']))])
        parent_id = categories_obj.search(['&', ('magento_website_id', '=', int(website.id)),('magento_id', '=', int(category['parent_id']))])
        if parent_id:
            vals = {
                'name': str(category['name']),
                'parent_id': int(parent_id.id),
                'magento_id': int(category['category_id']),
                'magento_website_id': website.id
            }
        else:
            vals = {
                'name': str(category['name']),
                'parent_id': False,
                'magento_id': int(category['category_id']),
                'magento_website_id': website.id
            }
        if not exist:
            categories_obj.create(vals)
            logging.info(website.name + ": Creata Categoria")
        else:
            exist.write(vals)
            logging.info(website.name + ": Aggiornata Categoria")


        for child in category['children']:
            self.recursive_category(child, website)


    def stock_magento(self):
        # Connect to WS Magento
        socket, session = self.connection()
        elenco_prodotti = []
        product_ids = self.env['product.product'].search([('magento_id', '!=', False)])
        for product in product_ids:
            elenco_prodotti.append(str(product.magento_id))
        stock_list = socket.call(session, "cataloginventory_stock_item.list", [elenco_prodotti])

        vals = {}
        vals['name'] = "Magento Inventory"
        vals['filter'] = "partial"

        id_inventory = self.env['stock.inventory'].create(vals)
        id_inventory.prepare_inventory()

        line = []

        for stock in stock_list:
            for product in product_ids:
                if str(product.magento_id) == (stock['product_id']):
                    # settings
                    if float(stock['qty']) >= 0:
                        line.append(
                            (0, 0, {'product_id': int(product.id), 'product_qty': float(stock['qty']), 'location_id': 15,
                                    'company_id': 1, 'inventory_id': int(id_inventory.id), 'product_uom_id': 1}))

        vals['line_ids'] = line
        id_inventory.write(vals)


        id_inventory.action_done()



    def process_customer_list(self, customer_list, magento_settings, socket, session, country_list):


        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with api.Environment.manage():
            new_cr.autocommit(True)
            self = self.with_env(self.env(cr=new_cr)).with_context(original_cr=self._cr)

            progresso = 0
            for customer in customer_list:
                progresso += 1
                if customer['customer_id']:
                    exist = False
                    try:
                        # Website
                        web_site = self.env['multi.magento.website'].search([('name', '=', magento_settings.url)], limit=1)
                        if not web_site:
                            web_site = self.env['multi.magento.website'].create(
                                {'name': website.url, 'url': website.url})

                        name = ''
                        email = ''
                        if 'firstname' in customer and 'lastname' in customer:
                            name = customer['firstname'] + " " + customer['lastname']
                        elif 'firstname' in customer and not 'lastname' in customer:
                            name = customer['firstname']
                        if 'email' in customer:
                            email = customer['email']

                        exist = self.env['res.partner'].search(['&', ('name', '=', name),('email', '=', email)])
                    except:
                        self.env.cr.rollback()



                    try:
                        if exist:
                            exist_website = False
                            for x in exist.magento_website_ids:
                                if x.magento_website_id.id == web_site.id:
                                    exist_website = True

                            if not exist_website:
                                exist.write({'magento_website_ids': [(0, 0, {'magento_website_id': web_site.id, 'magento_id': int(customer['customer_id'])})]})
                                logging.info(web_site.url+': Aggiornato Website Cliente')

                        if not exist:
                            customer_info = socket.call(session, "customer.info", [customer['customer_id']])
                            customer_address = socket.call(session, "customer_address.list", [customer['customer_id']])
                            customer_addresses = customer_address

                            vals = {}

                            vals['magento_website_ids'] = [(0, 0, {'magento_website_id': web_site.id, 'magento_id': int(customer['customer_id'])})]

                            #Se un customer ha un indirizzo, aggiungo i dati
                            if customer_address:
                                customer_address = customer_address[0]
                            if 'company' in customer_address:
                                vals['is_company'] = True
                            if 'fax' in customer_address:
                                vals['fax'] = customer_address['fax']
                            if 'postcode' in customer_address:
                                vals['zip'] = customer_address['postcode']
                            # if 'region' in customer_address:
                            if 'city' in customer_address:
                                vals['city'] = customer_address['city']
                            if 'street' in customer_address:
                                vals['street'] = customer_address['street']
                            if 'telephone' in customer_address:
                                vals['phone'] = customer_address['telephone']



                            if 'email' in customer:
                                vals['email'] = customer['email']
                            else:
                                vals['email'] = 'guest@guest.com'
                            if 'firstname' in customer and 'lastname' in customer:
                                vals['name'] = customer['firstname'] + " " + customer['lastname']
                            elif 'firstname' in customer and not 'lastname' in customer:
                                vals['name'] = customer['firstname']
                            elif not 'firstname' in customer:
                                vals['name'] = 'Guest'
                            if 'taxvat' in customer_info:
                                vals['vat'] = customer_info['taxvat']
                            if 'group_id' in customer_info:
                                group_id = self.env['magento.customers.group'].search([('magento_group_id', '=', int(customer_info['group_id']))])
                                if group_id:
                                    vals['magento_group'] = int(group_id.id)
                            if 'customer_id' in customer:
                                vals['magento_id'] = customer['customer_id']
                            if 'store_id' in customer_info:
                                store = self.env['magento.store'].search([('magento_id','=',int(customer_info['store_id']))])
                                if store:
                                    vals['store_id'] = store.id
                            if 'website_id' in customer_info:
                                vals['website_id'] = customer_info['website_id']
                            if 'firstname' in customer_info:
                                vals['mfirstname'] = customer_info['firstname']
                            if 'lastname' in customer_info:
                                vals['mlastname'] = customer_info['lastname']
                            if 'password' in customer_info:
                                vals['mpassword'] = customer_info['password']
                            if 'gender' in customer_info:
                                if customer_info['gender'] is not None:
                                    vals['mgender'] = int(customer_info['gender'])
                            if 'middlename' in customer_info:
                                vals['mmiddlename'] = customer_info['middlename']


                            if customer_address:

                                for country in country_list:
                                    if country['country_id'] == customer_address['country_id']:
                                        country_id = self.env['res.country'].search([('code', '=', country['iso2_code'])])
                                        if country_id:
                                            vals['country_id'] = int(country_id.id)
                                            country_id.write({'magento_id': str(country['country_id'])})

                                region_list = socket.call(session, "directory_region.list", [customer_address['country_id']])
                                for region in region_list:
                                    if region['region_id'] == customer_address['region_id']:
                                        state_id = self.env['res.country.state'].search([('code', '=', region['code'])])
                                        if state_id:
                                            vals['state_id'] = int(state_id[0].id)
                                            state_id[0].write({'magento_id': str(region['region_id'])})

                            cliente = False

                            if not exist:
                                #print("creato cliente")
                                cliente = self.env['res.partner'].create(vals)
                                cliente = cliente.id
                            else:
                                #print("aggiornato cliente")
                                exist.write(vals)
                                cliente = exist.id
                            self.env.cr.commit()


                            for address in customer_addresses:
                                vals_address = {}

                                exist_address = self.env['res.partner'].search(
                                    ['&', ('magento_id', '=', int(address['customer_address_id'])),
                                     ('magento_website_id', 'in', int(web_site.id))])

                                vals_address['parent_id'] = int(cliente)
                                vals_address['magento_website_id'] = int(web_site.id)
                                vals_address['magento_id'] = address['customer_address_id']
                                if 'firstname' in address and 'lastname' in address:
                                    vals_address['name'] = address['firstname'] + " " + address['lastname']
                                elif 'firstname' in address and not 'lastname' in address:
                                    vals_address['name'] = address['firstname']
                                elif not 'firstname' in address:
                                    vals_address['name'] = 'Guest'
                                if 'fax' in address:
                                    vals_address['fax'] = address['fax']
                                if 'postcode' in address:
                                    vals_address['zip'] = address['postcode']
                                if 'city' in address:
                                    vals_address['city'] = address['city']
                                if 'street' in address:
                                    vals_address['street'] = address['street']
                                if 'telephone' in address:
                                    vals_address['phone'] = address['telephone']
                                if bool(address['is_default_billing']) and bool(address['is_default_shipping']):
                                    break

                                if bool(address['is_default_billing']) and not bool(address['is_default_shipping']):
                                    vals_address['type'] = 'invoice'
                                if bool(address['is_default_shipping']) and not bool(address['is_default_billing']):
                                    vals_address['type'] = 'delivery'

                                if not exist_address:
                                    self.env['res.partner'].create(vals_address)
                                else:
                                    exist_address.write(vals_address)
                                self.env.cr.commit()

                                print("*****Creato Indirizzo Cliente********")


                            logging.info(str(progresso) + "/" + str(len(customer_list)))
                    except:
                        logging.info("Errore Durante Call Customers" + customer['customer_id'])


    def customer_magento(self):
        # Connect to WS Magento

        settings = self.getSettings()

        for website in settings:
            if not website.disable:
                socket, session = self.connection(website)
                customer_list = socket.call(session, "customer.list")
                country_list = socket.call(session, "directory_country.list")

                split_list = self.split_list(customer_list, 10)

                self.log_sync('Import Invoices')

                for list in split_list:
                    socket, session = self.connection(website)
                    if len(list) > 0:
                        t = threading.Thread(target=self.process_customer_list, args=(list, website, socket, session, country_list))
                        t.start()





    def process_invoice_list(self, invoice_list, magento_settings, socket, session):

        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with api.Environment.manage():
            new_cr.autocommit(True)
            self = self.with_env(self.env(cr=new_cr)).with_context(original_cr=self._cr)

            try:
                for invoice in invoice_list:
                    invoice_info = socket.call(session, "sales_order_invoice.info", [invoice['increment_id']])
                    order_info = socket.call(session, "sales_order.info", [invoice_info['order_increment_id']])
                    vals_invoice = {}
                    partner_id = False
                    # name = ''
                    if order_info and 'customer_id' in order_info:
                        # if 'billing_firstname' in order_info and 'billing_lastname' in order_info:
                        #     if order_info['billing_firstname']:
                        #         name += order_info['billing_firstname']
                        #     if order_info['billing_lastname'] and order_info['billing_firstname']:
                        #         name += " " + order_info['billing_lastname']
                        #     if order_info['billing_lastname'] and not order_info['billing_firstname']:
                        #         name += order_info['billing_lastname']
                        if order_info['customer_id'] != None:
                            partner_id = self.env['res.partner'].search(
                                [('magento_id', '=', int(order_info['customer_id']))])
                        if not partner_id:
                            # if name != '':
                            partner_id = self.env['res.partner'].search(
                                [('name', '=', 'Guest')])
                            if not partner_id:
                                partner_id = self.env['res.partner'].create({'name': 'Guest'})
                        if 'increment_id' in order_info:
                            vals_invoice['origin'] = str(order_info['increment_id'])
                        if partner_id:
                            lines_invoice = []
                            vals_invoice['partner_id'] = int(partner_id.id)

                            for item in invoice_info['items']:

                                # price = float(item['qty']) * float(item['price'])
                                # row_total = False
                                # if item['row_total']:
                                #     row_total = float(item['row_total'])
                                #
                                # discount = 0
                                # if price > 0 and row_total:
                                #     discount = 100 - ((row_total / price) * 100)


                                product_id = self.env['product.product'].search(
                                    [('magento_id', '=', int(item['product_id']))])
                                if product_id:
                                    product_id = product_id[0]
                                    lines_invoice.append(
                                        (0, 0, {'product_id': int(product_id.id), 'name': item['name'],
                                                'quantity': float(item['qty']),
                                                'account_id': int(magento_settings.magento_account_id.id),
                                                # 'discount': float(discount),
                                                'price_unit': float(item['price']),
                                                }))


                            # Aggiungo costo di spedizione
                            if 'shipping_amount' in invoice_info:
                                exist_shipping_product = self.env['product.product'].search(
                                    [('name', '=', 'Shipping & Handling')], limit=1)
                                if not exist_shipping_product:
                                    exist_shipping_product = self.env['product.product'].create(
                                        {'name': 'Shipping & Handling', 'categ_id': 3, 'magento_set': 1,
                                         'type': 'service', 'magento_type': 1})
                                lines_invoice.append((0, 0, {'product_id': int(exist_shipping_product.id),
                                                 'name': 'Shipping & Handling',
                                                 'quantity': 1.0,
                                                 'account_id': int(magento_settings.magento_account_id.id),
                                                 # 'tax_id': False,
                                                 'price_unit': float(
                                                     invoice_info['shipping_amount'])}))

                            # Aggiungo Sconto
                            if 'base_grand_total' in invoice_info and 'shipping_amount' in invoice_info:
                                if invoice_info['base_grand_total']:
                                    discount = (float(invoice_info['base_subtotal']) - float(invoice_info['base_grand_total'])) + float(invoice_info['shipping_amount'])
                                    exist_discount_product = self.env['product.product'].search(
                                        [('name', '=', 'Discount')], limit=1)
                                    if not exist_discount_product:
                                        exist_discount_product = self.env['product.product'].create(
                                            {'name': 'Discount', 'categ_id': 3, 'magento_set': 1,
                                             'type': 'service', 'magento_type': 1})
                                    lines_invoice.append(
                                        (0, 0, {'product_id': int(exist_discount_product.id),
                                                'name': 'Discount',
                                                'quantity': 1.0,
                                                'account_id': int(magento_settings.magento_account_id.id),
                                                # 'tax_id': False,
                                                'price_unit': - discount}))

                            # 1 aperta
                            # 2 pagata
                            # 3 cancellata

                            # if invoice_info['base_grand_total']:
                            #     vals_invoice['amount_total'] = float(invoice_info['base_grand_total'])

                            new_line = []
                            clean_line = []
                            clean_line.append((5,))
                            new_line.extend(clean_line)
                            new_line.extend(lines_invoice)
                            if 'state' in invoice_info:

                                if invoice_info['state'] != '2':
                                    vals_invoice['invoice_line_ids'] = new_line

                                if invoice_info['state'] == '1':
                                    vals_invoice['state'] = 'open'
                                if invoice_info['state'] == '2':
                                    vals_invoice['state'] = 'paid'
                                if invoice_info['state'] == '3':
                                    vals_invoice['state'] = 'cancel'

                            if 'created_at' in invoice_info:
                                vals_invoice['date_invoice'] = invoice_info['created_at']

                            vals_invoice['magento_id'] = str(invoice['increment_id'])
                            vals_invoice['name'] = invoice['increment_id']
                            vals_invoice['number'] = invoice['increment_id']

                            # Creo anche il preventivo se nelle impostazioni e' abilitato
                            if magento_settings:
                                # Prendo i valori di default
                                vals_invoice['account_id'] = int(magento_settings.magento_account_id.id)
                                vals_invoice['company_id'] = int(magento_settings.magento_company_id.id)
                                vals_invoice['currency_id'] = int(magento_settings.magento_currency_id.id)
                                vals_invoice['journal_id'] = int(magento_settings.magento_journal_id.id)

                            # Website
                            website = self.env['multi.magento.website'].search([('name', '=', magento_settings.url)], limit=1)
                            if not website:
                                website = self.env['multi.magento.website'].create(
                                    {'name': website.url, 'url': website.url})

                            vals_invoice['magento_website_id'] = website.id

                            exist_invoice = self.env['account.invoice'].search(['&', ('magento_id', '=', int(invoice['increment_id'])),('magento_website_id', '=', int(website.id))])
                            if not exist_invoice:
                                # Se deve essere creata aggiungo tutte le righe senza prima svuotare
                                vals_invoice['invoice_line_ids'] = lines_invoice
                                self.env['account.invoice'].create(vals_invoice)
                                logging.info('Creata: ' + invoice['increment_id'])
                            else:
                                exist_invoice.write(vals_invoice)
                                logging.info('Modificata: ' + invoice['increment_id'])
                            self.env.cr.commit()
            finally:
                print("terminato")
                # self.env.cr.close()



    def invoice_magento(self):
        # Connect to WS Magento
        settings = self.getSettings()

        for website in settings:
            # socket, session = self.connection()
            # magento_settings = self.env['magento.settings'].search([('id', '=', 1)])
            filters = {}

            thread_blocks = []
            current_year = date.today().year
            start_year = 2000
            big_list = []
            n = 0

            while start_year <= current_year:
                filters = {'created_at':
                    {
                        'from': str(start_year) + '-01-01 00:00:00',
                        'to': str(start_year + 1) + '-12-31 23:59:00'
                    },
                }
                start_year += 2
                thread_blocks.append(filters)

            for filter in thread_blocks:
                socket, session = self.connection(website)
                invoice_list = socket.call(session, "sales_order_invoice.list", [filter])
                big_list.extend(invoice_list)
                n += 1

            split_list = self.split_list(big_list, 1)

            self.log_sync('Import Invoices')

            for list in split_list:
                socket, session = self.connection(website)
                if len(list) > 0:
                    t = threading.Thread(target=self.process_invoice_list, args=(list, website, socket, session,))
                    t.start()







    def split_list(self, list, n):
        avg = len(list) / float(n)
        out = []
        last = 0.0

        while last < len(list):
            out.append(list[int(last):int(last + avg)])
            last += avg

        return out


    def process_sale_order(self, sale_order_list, magento_settings, socket, session):
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        with api.Environment.manage():
            new_cr.autocommit(True)
            self = self.with_env(self.env(cr=new_cr)).with_context(original_cr=self._cr)
            try:
                website = self.env['multi.magento.website'].search([('name', '=', magento_settings.url)], limit=1)
                if not website:
                    website = self.env['multi.magento.website'].create({'name': website.url, 'url': website.url})
                crm_team_id = self.env['crm.team'].search([('name', '=', 'Website Sales')])
                shipping_service_id = self.env['product.product'].search([('name', '=', 'Shipping & Handling')],limit=1)
                cashondelivery_id = self.env['product.product'].search([('name', '=', 'Cash on Delivery')],limit=1)
                base_discount_amount_id = self.env['product.product'].search([('name', '=', 'Discount Amount')],limit=1)
                for order in sale_order_list:
                    exist = self.env['sale.order'].search(['&', ('magento_id', '=', str(order['increment_id'])),('magento_website_id', '=', int(website.id))])
                    if not exist:
                        sale_order_info = socket.call(session, "sales_order.info", [order['increment_id']])
                        partner_id = False #Partner

                        if 'customer_id' in sale_order_info:
                            if sale_order_info['customer_id']:
                                partner_id = self.env['res.partner'].search(['&',('magento_website_ids.magento_website_id.id', '=', int(website.id)),('magento_id', '=', int(sale_order_info['customer_id']))], limit=1)
                            else:
                                if 'shipping_address' in sale_order_info:
                                    if sale_order_info['shipping_address']:
                                        indirizzo_spedizione = sale_order_info['shipping_address']
                                        name_customer = ''
                                        if 'firstname' in indirizzo_spedizione:
                                            if indirizzo_spedizione['firstname']:
                                                name_customer += indirizzo_spedizione['firstname']
                                        if 'lastname' in indirizzo_spedizione:
                                            if indirizzo_spedizione['lastname']:
                                                name_customer += " " + indirizzo_spedizione['lastname']
                                        partner_street = ''
                                        if 'street' in indirizzo_spedizione:
                                            if indirizzo_spedizione['street']:
                                                partner_street = indirizzo_spedizione['street']
                                        partner_city = ''
                                        if 'city' in indirizzo_spedizione:
                                            if indirizzo_spedizione['city']:
                                                partner_city = indirizzo_spedizione['city']
                                        partner_zip = False
                                        if 'postcode' in indirizzo_spedizione:
                                            if indirizzo_spedizione['postcode']:
                                                partner_zip = indirizzo_spedizione['postcode']
                                        partner_magento_id = int(sale_order_info['shipping_address_id'])
                                        vals_partner = {
                                            'name': name_customer,
                                            'street': partner_street,
                                            'city': partner_city,
                                            'zip': partner_zip,
                                            'magento_id': partner_magento_id,
                                            'magento_website_ids': [0, 0, {'magento_website_id': website.id, 'magento_id': partner_magento_id}]
                                        }
                                        partner_id = self.env['res.partner'].create(vals_partner)
                                        del vals_partner
                            if partner_id:
                                lines = []
                                # Prodotti
                                for item in sale_order_info['items']:
                                    product_id = self.env['product.product'].search(['&', ('magento_website_ids.magento_website_id.id', '=', int(website.id)), ('magento_website_ids.magento_id', '=', int(item['product_id']))], limit=1)
                                    if product_id:
                                        #Calcola sconto riga
                                        lines.append((0, 0, {'product_id': int(product_id.id), 'name': item['name'],
                                                             'product_uom_qty': float(item['qty_ordered']),
                                                             'tax_id': False,
                                                             'discount': float(item['discount_percent']),
                                                             'price_unit': float(item['price'])}))
                                #Aggiungo costo di spedizione
                                if 'base_shipping_amount' in sale_order_info:
                                    if not shipping_service_id:
                                        shipping_service_id = self.env['product.product'].create({'name': 'Shipping & Handling', 'categ_id': 3, 'magento_set': 1, 'type': 'service', 'magento_type': 1})
                                    lines.append((0, 0, {'product_id': int(shipping_service_id.id), 'name': shipping_service_id.name,
                                                         'product_uom_qty': 1.0,
                                                         'tax_id': False,
                                                         'price_unit': float(sale_order_info['base_shipping_amount'])}))
                                #Aggiungo Contrassegno
                                if 'msp_cashondelivery_incl_tax' in sale_order_info:
                                    if sale_order_info['msp_cashondelivery_incl_tax']:
                                        if not cashondelivery_id:
                                            cashondelivery_id = self.env['product.product'].create(
                                                {'name': 'Cash on Delivery', 'categ_id': 3, 'magento_set': 1,
                                                 'type': 'service', 'magento_type': 1})
                                        lines.append((0, 0, {'product_id': int(cashondelivery_id.id),
                                                             'name': cashondelivery_id.name,
                                                             'product_uom_qty': 1.0,
                                                             'tax_id': False,
                                                             'price_unit': float(
                                                                 sale_order_info['msp_cashondelivery_incl_tax'])}))
                                # Aggiungo Eventuale Sconto Sull'intero ordine
                                if 'base_discount_amount' in sale_order_info:
                                    if sale_order_info['base_discount_amount']:
                                        if not base_discount_amount_id:
                                            base_discount_amount_id = self.env['product.product'].create(
                                                {'name': 'Discount Amount', 'categ_id': 3, 'magento_set': 1,
                                                 'type': 'service', 'magento_type': 1})
                                        lines.append((0, 0, {'product_id': int(base_discount_amount_id.id),
                                                             'name': base_discount_amount_id.name,
                                                             'product_uom_qty': 1.0,
                                                             'tax_id': False,
                                                             'price_unit': float(sale_order_info['base_discount_amount'])}))


                                # Svuoto tutte le vecchie righe
                                new_line = [(5,)]
                                new_line.extend(lines)

                                if 'status' in sale_order_info:
                                    if sale_order_info['status'] == 'canceled':
                                        order_state = 'cancel'
                                    if sale_order_info['status'] == 'complete':
                                        order_state = 'sale'
                                    if sale_order_info['status'] == 'processing':
                                        order_state = 'sent'
                                    if sale_order_info['status'] == 'pending':
                                        order_state = 'draft'
                                    if sale_order_info['status'] == 'onhold':
                                        order_state = 'done'

                                date_order = False
                                if 'created_at' in sale_order_info:
                                    date_order = sale_order_info['created_at']

                                order_magento_id = str(order['increment_id'])

                                order_name = ''
                                if magento_settings:
                                    if 'magento_sale_order_prefix' in magento_settings:
                                        if magento_settings['magento_sale_order_prefix']:
                                            order_name = str(magento_settings['magento_sale_order_prefix']) + order['increment_id']
                                        else:
                                            order_name = order['increment_id']

                                #Visible on Website Admin
                                team_id = False
                                if crm_team_id and magento_settings.magento_sale_order_from_ecommerce:
                                    team_id = int(crm_team_id[0].id)

                                vals = {
                                    'name': order_name,
                                    'partner_id': partner_id.id,
                                    'magento_website_id': int(website.id),
                                    'order_line': new_line,
                                    'team_id': team_id,
                                    'magento_id': order_magento_id,
                                    'date_order': date_order,
                                    'state': order_state,
                                }

                                if not exist:
                                    try:
                                        self.env['sale.order'].create(vals)
                                        logging.info('creato: ' + vals['name'])
                                    except:
                                        print("errore ordine: " + vals['name'])
                                        self.env.cr.rollback()
                                else:
                                    exist.write(vals)
                                    logging.info('modificato: ' + vals['name'])

                                del vals
                                self.env.cr.commit()
            except:
                print("Order Error")
                self.env.cr.rollback()
            finally:
                print("Terminated")
                #self.env.cr.close()



    def sale_order_magento(self):
        # Connect to WS Magento
        settings = self.getSettings()

        for website in settings:
            if not website.disable:
                thread_blocks = []
                current_year = date.today().year + 1
                start_year = 2010
                big_list = []
                n = 0

                only_from = ""
                only_to = ""
                if website.magento_sale_order_from:
                    only_from = website.magento_sale_order_from

                if website.magento_sale_order_to:
                    only_to = website.magento_sale_order_to


                while start_year <= current_year:
                    filters = {'created_at':
                        {
                            'from': str(start_year)+'-01-01 00:00:00' if not website.magento_sale_order_from else only_from,
                            'to': str(start_year+1)+ '-12-31 23:59:00' if not website.magento_sale_order_to else only_to
                        },
                    }
                    if website.magento_sale_order_status:
                        filters['status'] = str(website.magento_sale_order_status)
                    start_year += 2
                    thread_blocks.append(filters)

                socket, session = self.connection(website)
                for filter in thread_blocks:
                    try:
                        sale_order_list = socket.call(session, "sales_order.list", [filter])
                        big_list.extend(sale_order_list)
                        n += 1
                    except:
                        print("errore 500: ")

                # socket, session = self.connection(website)
                # sale_order_list = socket.call(session, "sales_order.list", [])
                # big_list.extend(sale_order_list)

                split_list = self.split_list(big_list, 5)
                self.log_sync('Import Sales Order')


                for list in split_list:
                    socket, session = self.connection(website)
                    if len(list)>0:
                        t = threading.Thread(target=self.process_sale_order, args=(list, website, socket, session,))
                        t.start()

    def RepresentsInt(self,s):
        try:
            if not isinstance(s, (list,tuple)):
                int(s)
                return True
            else:
                return False
        except ValueError:
            return False


    def attribute_magento(self):
        # Connect to WS Magento

        settings = self.getSettings()

        for website in settings:
            socket, session = self.connection(website)
            attributes_set = socket.call(session, "catalog_product_attribute_set.list")
            attribute_obj = self.env['product.attribute']

            web_site = self.env['multi.magento.website'].search([('name', '=', website.url)], limit=1)
            if not web_site:
                web_site = self.env['multi.magento.website'].create({'name': website.url, 'url': website.url})

            for attribute_set in attributes_set:
                ####Creazione Attribute Set######
                attributes_set_exist = self.env['magento.attribute.set'].search(['&', ('magento_website_id', '=', int(web_site.id)),
                    ('magento_id', '=', int(attribute_set['set_id']))])
                vals_set = {'magento_id': attribute_set['set_id'], 'name': attribute_set['name'], 'magento_website_id': web_site.id}
                if not attributes_set_exist:
                    self.env['magento.attribute.set'].create(vals_set)
                else:
                    attributes_set_exist.write(vals_set)
                ####Attributi di Attribute Set#####
                attributes = socket.call(session, "catalog_product_attribute.list", [int(attribute_set['set_id'])])
                for attribute in attributes:
                    print("Fatto")
                    exist = attribute_obj.search(['&', ('magento_website_id', '=', int(web_site.id)),('magento_id', '=', attribute['attribute_id'])])
                    # Attribute Values
                    if 'attribute_id' in attribute and attribute['code'] != 'allow_open_amount' and attribute['code'] != 'giftcard_type':
                        attribute_values = False
                        try:
                            attribute_values = socket.call(session, 'product_attribute.info', [str(attribute['attribute_id'])])
                        except int:
                            self.env.cr.rollback()
                        if attribute_values:
                            # Se il prodotto e' visibile lo aggiungo/modifico
                            # if int(attribute_values['is_visible_on_front']) == 1:

                            vals = {}
                            vals['magento_website_id'] = web_site.id
                            if 'code' in attribute:
                                vals['name'] = attribute['code']
                            if 'attribute_id' in attribute:
                                vals['magento_id'] = attribute['attribute_id']
                            if 'type' in attribute:
                                if attribute['type'] == 'select' or attribute['type'] == 'color':
                                    vals['type'] = attribute['type']
                                else:
                                    vals['type'] = 'radio'
                            vals['magento_default_value'] = attribute_values['default_value']
                            vals['magento_is_unique'] = True if attribute_values['is_unique'] == "1" else False
                            vals['magento_is_required'] = True if attribute_values['is_required'] == "1" else False
                            vals['magento_is_configurable'] = True if attribute_values['is_configurable'] == "1" else False
                            vals['magento_is_searchable'] = True if attribute_values['is_searchable'] == "1" else False
                            vals['magento_is_visible_in_advanced_search'] = True if attribute_values['is_visible_in_advanced_search'] == "1" else False
                            vals['magento_is_comparable'] = True if attribute_values['is_comparable'] == "1" else False
                            vals['magento_is_used_for_promo_rules'] =True if attribute_values['is_used_for_promo_rules'] == "1" else False
                            vals['magento_is_visible_on_front'] = True if attribute_values['is_visible_on_front'] == "1" else False
                            vals['magento_used_in_product_listing'] = True if attribute_values['used_in_product_listing'] == "1" else False

                            # Collego l'id dell'attribute set al campo many2many
                            set_id = self.env['magento.attribute.set'].search(
                                [('magento_id', '=', int(attribute_set['set_id']))])
                            if set_id:
                                vals['attribute_set_ids'] = [(4, int(set_id.id))]

                            # Creo l'attributo
                            if not exist:
                                attribute_obj.create(vals)
                                print("Creato Attributo")
                            # Aggiorno l'attributo
                            else:
                                exist.write(vals)
                                print("Aggiornato Attributo")

                            # Aggiungo Option
                            attribute_option_obj = self.env['product.attribute.value']
                            try:
                                options = socket.call(session, "catalog_product_attribute.options",
                                                      [str(attribute['attribute_id'])])

                                for option in options:
                                    if 'value' in option:
                                        if option['value'] != '' and self.RepresentsInt(option['value']):
                                            exist = attribute_option_obj.search([('name', '=', option['label'])])
                                            id_attribute = attribute_obj.search(['&', ('magento_website_id', '=', int(web_site.id)),('magento_id', '=', attribute['attribute_id'])])

                                            vals = {}
                                            vals['magento_website_id'] = web_site.id
                                            # Associazione Attributo
                                            if id_attribute:
                                                vals['attribute_id'] = int(id_attribute.id)
                                            # Valore associato all'attributo
                                            if 'label' in option:
                                                vals['name'] = option['label']
                                            if 'value' in option:
                                                vals['magento_id'] = int(option['value'])

                                            if not exist:
                                                attribute_option_obj.create(vals)
                                            else:
                                                exist.write(vals)
                                            self.env.cr.commit()
                            except:
                                self.env.cr.rollback()


    def log_sync(self, text):
        ls_id = self.env['magento.sync.log'].search([('id', '=', 1)])
        if not ls_id:
            ls_id = self.env['magento.sync.log'].create({'id': 1})

        tst = '<span><strong style="color: orange;">' + str(date.today()) + ': </strong></span>'
        tst += '<span>' + text + '</span><br/>'

        if ls_id.log:
            ls_id.log += tst
        else:
            ls_id.log = tst



    #Variabile globale per contare il numero dei prodotti processati

    def process_product_list(self,product_list, website, socket, session, list_size):


        copia_lista = product_list

        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with api.Environment.manage():
            new_cr.autocommit(True)
            self = self.with_env(self.env(cr=new_cr)).with_context(original_cr=self._cr)
            #self.env = api.Environment(new_cr, uid, context)
            product_obj = self.env['product.product']

            try:


                for product in product_list:




                    web_site = self.env['multi.magento.website'].search([('name', '=', website.url)], limit=1)
                    if not web_site:
                        web_site = self.env['multi.magento.website'].create(
                            {'name': website.url, 'url': website.url})

                    # if 'sku' in product:
                    #     if not product['sku']:
                    #         logging.info(product['product_id'])

                    if 'sku' in product:
                        if product['sku']:

                            copia_lista.pop(cont)

                            #Controllo se siste
                            exist = product_obj.search([('default_code', '=', str(product['sku']))])

                            #Se esiste ci aggiungo il magento_website_id
                            if exist:



                                exist_website = False
                                for x in exist.magento_website_ids:
                                    if x.magento_website_id.id == web_site.id:
                                        exist_website = True

                                if exist_website:
                                    logging.info(web_site.name + ": Prodotto OK : ")

                                if not exist_website:
                                    exist.write({
                                        'magento_website_ids': [(0, 0, {'magento_website_id': web_site.id, 'magento_id': int(product['product_id'])})]
                                    })
                                    logging.info(web_site.name + ": Aggiornato Website Prodotto: ")
                                    self.env.cr.commit()

                            #Altrimento lo creo
                            if not exist:


                                # Product Extra
                                extra_info = False
                                try:
                                    extra_info = socket.call(session, 'catalog_product.info', [str(product['product_id'])])
                                except:
                                    # logging.info(product)
                                    logging.info(product['sku'])
                                    self.env.cr.rollback()

                                # logging.info('Extra Info OK')
                                if extra_info:
                                    category = self.env['product.category'].search(
                                        [('magento_id', 'in', extra_info['category_ids'])])

                                    vals = {}
                                    # Inserisco se esistono tutti i vari campi
                                    vals['magento_website_ids'] = [(0, 0, {'magento_website_id': web_site.id, 'magento_id': int(product['product_id'])})]
                                    if 'sku' in product:
                                        vals['default_code'] = product['sku']
                                    if 'product_id' in product:
                                        vals['magento_id'] = int(product['product_id'])
                                    if 'name' in product:
                                        if product['name']:
                                            vals['name'] = product['name']
                                        else:
                                            vals['name'] = 'default'
                                    else:
                                        vals['name'] = 'default'
                                    if 'price' in extra_info:
                                        if isinstance(extra_info['price'], str):
                                            vals['list_price'] = float(extra_info['price'])
                                    if category:
                                        # Imposto la categoria singola di odoo
                                        vals['categ_id'] = int(category[0].id)
                                    else:
                                        #Non esiste nessuna categoria, Setto la radice principale
                                        vals['categ_id'] = 3
                                    # Imposto le categorie multiple di Magento
                                    categories = []
                                    for category in extra_info['category_ids']:
                                        category_id = self.env['product.category'].search(['&',('magento_id', '=', int(category)),('magento_website_id', '=', int(web_site.id))], limit=1)
                                        if category_id:
                                            categories.append((4, int(category_id.id)))
                                    vals['magento_category_ids'] = categories
                                    if 'description' in extra_info:
                                        vals['description_sale'] = extra_info['description']
                                    if 'status' in extra_info:
                                        if extra_info['status'] == '2':
                                            vals['magento_status'] = False
                                        else:
                                            vals['magento_status'] = bool(extra_info['status'])
                                    if 'weight' in extra_info:
                                        vals['magento_weight'] = extra_info['weight']
                                        if isinstance(extra_info['weight'], str) or isinstance(extra_info['weight'], float) or isinstance(extra_info['weight'], int):
                                            vals['weight'] = float(extra_info['weight'])
                                    if 'visibility' in extra_info:
                                        if extra_info['visibility'] == '0':
                                            vals['magento_visibility'] = False
                                        else:
                                            vals['magento_visibility'] = bool(extra_info['visibility'])
                                    if 'special_price' in extra_info:
                                        if extra_info['special_price'] >= 0:
                                            vals['magento_special_price'] = float(extra_info['special_price'])
                                    if 'set' in extra_info:
                                        set_id = self.env['magento.attribute.set'].search(
                                            [('magento_id', '=', int(extra_info['set']))])
                                        if set_id:
                                            vals['magento_set'] = int(set_id.id)
                                    if 'type' in extra_info:
                                        type_id = self.env['magento.product.type'].search([('type', '=', str(extra_info['type']))])
                                        if type_id:
                                            vals['magento_type'] = int(type_id.id)
                                    if 'special_price' in extra_info:
                                        if extra_info['special_price'] is not None:
                                            vals['magento_special_price'] = float(extra_info['special_price'])
                                    if 'special_from_date' in extra_info:
                                        if extra_info['special_from_date'] is not None:
                                            vals['magento_special_from_date'] = str(extra_info['special_from_date'])
                                    if 'special_to_date' in extra_info:
                                        if extra_info['special_to_date'] is not None:
                                            vals['magento_special_to_date'] = str(extra_info['special_to_date'])
                                    if 'meta_title' in extra_info:
                                        try:
                                            vals['magento_meta_title'] = str(extra_info['meta_title'])
                                        except:
                                            print('non convertito')
                                    if 'meta_description' in extra_info:
                                        description = extra_info['meta_description']
                                        vals['magento_meta_description'] = description
                                    if 'meta_keyword' in extra_info:
                                        try:
                                            vals['magento_meta_keyword'] = str(extra_info['meta_keyword'])
                                        except:
                                            print('non convertito')
                                    if 'custom_design' in extra_info:
                                        vals['magento_custom_design'] = str(extra_info['custom_design'])

                                    # #Per customer group
                                    # if 'tier_price' in extra_info:
                                    #     tier_price = []
                                    #     for t in extra_info['tier_price']:
                                    #         tier_price_line = {}
                                    #         if 'customer_group_id' in t:
                                    #             customer_group = self.env['magento.customers.group'].search([('magento_group_id','=', int(t['customer_group_id']))])
                                    #             if customer_group:
                                    #                 customer_group = customer_group[0]
                                    #                 tier_price_line['customer_group'] = customer_group.id
                                    #         if 'website' in t:
                                    #             tier_price_line['website'] = t['website']
                                    #         if 'qty' in t:
                                    #             tier_price_line['qty'] = float(t['qty'])
                                    #         if 'price' in t:
                                    #             tier_price_line['cost'] = float(t['price'])
                                    #         tier_price.append((0, 0, tier_price_line))
                                    #
                                    # vals['magento_tier_price'] = tier_price



                                    # Odoo Type
                                    vals['type'] = 'product'

                                    # Il prodotto non esiste, lo creo
                                    product_id = False
                                    if not exist:
                                        product_id = product_obj.create(vals)
                                    # Il prodotto esiste, aggiorno i campi
                                    else:
                                        exist.write(vals)


                                    self.env.cr.commit()
                                    logging.info(web_site.name + ": Importato Prodotto: ")


            finally:
                logging.info("Chiudo: ")
                self.env.cr.close()


    def product_magento(self):
        # Connect to WS Magento

        settings = self.getSettings()

        for website in settings:
            if not website.disable:
                thread_blocks = []
                big_list = []
                n = 0
                alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'

                for l in alphabet:
                    filters = {
                        'sku': {'like': l+"%"}
                    }
                    thread_blocks.append(filters)



                for filter in thread_blocks:
                    socket, session = self.connection(website)
                    products_list = socket.call(session, "catalog_product.list", [filter])
                    big_list.extend(products_list)
                    n += 1


                split_list = self.split_list(big_list,1)

                self.log_sync('Import Products')

                for list in split_list:
                    socket, session = self.connection(website)
                    if len(list) > 0:
                        t = threading.Thread(target=self.process_product_list, args=(list, website, socket, session, len(big_list)))
                        t.start()





    def product_images(self):

        settings = self.getSettings()

        for website in settings:
            if not website.disable:

                socket, session = self.connection(website)
                #Elimino tutte le foto dal database:

                web_site = self.env['multi.magento.website'].search([('name', '=', website.url)], limit=1)
                if not web_site:
                    web_site = self.env['multi.magento.website'].create(
                        {'name': website.url, 'url': website.url})

                self.env.cr.execute('delete from ir_attachment where magento_id = true and magento_website_id = ' + str(web_site.id))
                magento_product_ids = self.env['product.product'].search(['&', ('magento_id', '!=', False), ('magento_website_ids.magento_website_id', '=', web_site.id)])
                for product in magento_product_ids:
                    magento_id = ''
                    for mid in product.magento_website_ids:
                        if mid.magento_website_id.id == web_site.id:
                            magento_id = mid.magento_id
                    if magento_id:
                        media = socket.call(session, 'catalog_product_attribute_media.list', [str(magento_id)])
                        # Download Photos
                        images = []
                        base64_array = []
                        for photo in media:
                            if 'url' in photo:
                                url = photo['url']
                                filename = url.split('/')[-1]
                                file = requests.get(str(url), stream=True)
                                if file.status_code == 200:
                                    vals_p = {'datas': base64.b64encode(file.content),
                                              'name': filename,
                                              'url': url,
                                              'datas_fname': filename,
                                              'res_model': 'product.template',
                                              'magento_website_id': web_site.id,
                                              'magento_id': True,
                                              'res_id': 0}

                                    base64_array.append(vals_p)

                                    attachment = self.env['ir.attachment'].create(vals_p)
                                    if attachment:
                                        # Aggiunto al prodotto
                                        # images.append(int(attachment.id))
                                        images.append((4, int(attachment.id)))

                        # Il prodotto non esisteva, e' stato creato e lo aggiorno con le foto
                        product.write({'magento_images_ids': images})


                        image_type = ['image', 'image_medium', 'image_small']
                        # Imposto La foto del prodotto
                        if len(base64_array) > 0:
                            first_photo = base64_array[0]
                            first_photo['res_model'] = 'product.template'
                            # first_photo['res_id'] = int(product.id)
                            esiste_foto_prodotto = self.env['ir.attachment'].search(['&', ('res_model', '=', 'product.template'), ('res_id', '=', int(product.id))])
                            product_id = self.env['product.product'].search([('id', '=', int(int(product.id)))])
                            esiste_foto_template = False
                            if product_id:
                                esiste_foto_template = int(product_id.product_tmpl_id)
                                first_photo['res_id'] = int(product_id.product_tmpl_id)
                            # creo i 3 tipi di immagini
                            for type in image_type:
                                first_photo['res_field'] = type
                                first_photo['name'] = type
                                if esiste_foto_prodotto and esiste_foto_template:
                                    esiste_foto_prodotto.write(first_photo)
                                if not esiste_foto_prodotto and esiste_foto_template:
                                    self.env['ir.attachment'].create(first_photo)

                        self.env.cr.commit()
