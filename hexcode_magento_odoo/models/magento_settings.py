import requests

from odoo import models, api, fields
from odoo.osv import osv


#Impostazioni di Magento
class magento_settings(models.Model):
    _name = 'magento.settings'

    url = fields.Char(String="Url Magento")
    username = fields.Char(String="Web Service Username")
    password = fields.Char(String="Web Service Password")
    import_categories_interval_time = fields.Integer()
    import_categories_interval_units = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months')])
    import_attributes_interval_time = fields.Integer()
    import_attributes_interval_units = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months')])
    import_customers_interval_time = fields.Integer()
    import_customers_interval_units = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months')])
    import_products_interval_time = fields.Integer()
    import_products_interval_units = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months')])
    import_products_stock_interval_time = fields.Integer()
    import_products_stock_interval_units = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months')])
    import_sales_orders_interval_time = fields.Integer()
    import_sales_orders_interval_units = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months')])

    magento_sale_order_prefix = fields.Char()
    magento_invoice_prefix = fields.Char()
    magento_sale_order_status = fields.Selection(selection=[('canceled', 'Canceled'), ('pending', 'Pending'),('complete', 'Complete'),
                                                            ('processing', 'Processing'),('onhold', 'On Hold')])
    magento_customer_email = fields.Char()
    magento_product_simple_product = fields.Boolean()
    magento_sale_order_from = fields.Datetime()
    magento_sale_order_to = fields.Datetime()
    magento_sale_order_auto_invoice = fields.Boolean()

    magento_account_id = fields.Many2one('account.account')
    magento_company_id = fields.Many2one('res.company')
    magento_currency_id = fields.Many2one('res.currency')
    magento_journal_id = fields.Many2one('account.journal')

    magento_sale_order_from_ecommerce = fields.Boolean(default=False)
    magento_licenze_key = fields.Char()
    disable = fields.Boolean()


    @api.onchange('magento_licenze_key')
    def onchange_license(self):
        self.magento_license_action()

    @api.one
    def magento_license_action(self):
        if self.magento_licenze_key:
            payload = {'license': self.magento_licenze_key}
            r = requests.get('https://www.hexcode.it/odoo_module/magento_connector_license.php', params=payload)
            if r.text == 'verified':
                print("ok verified")
            else:
                self.magento_licenze_key = False


# class YourSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#     _name = 'magento.odoo.settings'
#
#     company_name = fields.Char()
#     company_phone = fields.Char()
#     magento_url = fields.Char()
#     magento_ws_user = fields.Char()
#     magento_psw_user = fields.Char()
#
#     #CRON
#     import_categories_interval_time = fields.Integer()
#     import_categories_interval_units = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
#                                                          ('weeks', 'Weeks'), ('months', 'Months')])
#     import_attributes_interval_time = fields.Integer()
#     import_attributes_interval_units = fields.Selection(
#         [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
#          ('weeks', 'Weeks'), ('months', 'Months')])
#     import_customers_interval_time = fields.Integer()
#     import_customers_interval_units = fields.Selection(
#         [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
#          ('weeks', 'Weeks'), ('months', 'Months')])
#     import_products_interval_time = fields.Integer()
#     import_products_interval_units = fields.Selection(
#         [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
#          ('weeks', 'Weeks'), ('months', 'Months')])
#     import_products_stock_interval_time = fields.Integer()
#     import_products_stock_interval_units = fields.Selection(
#         [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
#          ('weeks', 'Weeks'), ('months', 'Months')])
#     import_sales_orders_interval_time = fields.Integer()
#     import_sales_orders_interval_units = fields.Selection(
#         [('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days', 'Work Days'), ('days', 'Days'),
#          ('weeks', 'Weeks'), ('months', 'Months')])
#
#
#
#     magento_sale_order_prefix = fields.Char()
#     magento_invoice_prefix = fields.Char()
#     magento_sale_order_status = fields.Selection(selection=[('canceled', 'Canceled'), ('pending', 'Pending'),('complete', 'Complete'),
#                                                             ('processing', 'Processing'),('onhold', 'On Hold')])
#     magento_sale_order_from = fields.Datetime()
#     magento_sale_order_to = fields.Datetime()
#     magento_product_simple_product = fields.Boolean()
#     magento_customer_email = fields.Char()
#     magento_sale_order_auto_invoice = fields.Boolean()
#
#     magento_account_id = fields.Many2one('account.account')
#     magento_company_id = fields.Many2one('res.company')
#     magento_currency_id = fields.Many2one('res.currency')
#     magento_journal_id = fields.Many2one('account.journal')
#
#     magento_sale_order_from_ecommerce = fields.Boolean(default=False)
#     magento_licenze_key = fields.Char()
#     enable_multi_website = fields.Boolean()
#     magento_website_ids = fields.Many2many('multi.magento.website')
#
#
#     @api.onchange('magento_licenze_key')
#     def onchange_license(self):
#         self.magento_license_action()
#
#     @api.one
#     def magento_license_action(self):
#         if self.magento_licenze_key:
#             payload = {'license': self.magento_licenze_key}
#             r = requests.get('https://www.hexcode.it/odoo_module/magento_connector_license.php', params=payload)
#             if r.text == 'verified':
#                 print("ok verified")
#             else:
#                 self.magento_licenze_key = False
#
#     @api.model
#     def get_default_settings(self, fields):
#         company = self.env.user.company_id
#         magento_settings = self.env['magento.settings'].search([('id', '=', 1)])
#         if not magento_settings:
#             magento_settings = self.env['magento.settings'].create({})
#
#         magento_website_ids = []
#         for website in magento_settings.magento_website_ids:
#             magento_website_ids.append((4, website))
#
#         return {
#             'company_name': company.name,
#             'company_phone': company.phone,
#             'magento_url': magento_settings.url,
#             'magento_ws_user': magento_settings.username,
#             'magento_psw_user': magento_settings.password,
#             'import_categories_interval_time': magento_settings.import_categories_interval_time,
#             'import_categories_interval_units': magento_settings.import_categories_interval_units,
#             'import_attributes_interval_time': magento_settings.import_attributes_interval_time,
#             'import_attributes_interval_units': magento_settings.import_attributes_interval_units,
#             'import_customers_interval_time': magento_settings.import_customers_interval_time,
#             'import_customers_interval_units': magento_settings.import_customers_interval_units,
#             'import_products_interval_time': magento_settings.import_products_interval_time,
#             'import_products_interval_units': magento_settings.import_products_interval_units,
#             'import_products_stock_interval_time': magento_settings.import_products_stock_interval_time,
#             'import_products_stock_interval_units': magento_settings.import_products_stock_interval_units,
#             'import_sales_orders_interval_time': magento_settings.import_sales_orders_interval_time,
#             'import_sales_orders_interval_units': magento_settings.import_sales_orders_interval_units,
#             'magento_sale_order_prefix': magento_settings.magento_sale_order_prefix,
#             'magento_sale_order_status': magento_settings.magento_sale_order_status,
#             'magento_customer_email': magento_settings.magento_customer_email,
#             'magento_product_simple_product': magento_settings.magento_product_simple_product,
#             'magento_sale_order_from': magento_settings.magento_sale_order_from,
#             'magento_sale_order_to': magento_settings.magento_sale_order_to,
#             'magento_sale_order_auto_invoice': magento_settings.magento_sale_order_auto_invoice,
#             'magento_invoice_prefix': magento_settings.magento_invoice_prefix,
#             'magento_account_id': magento_settings.magento_account_id.id,
#             'magento_company_id': magento_settings.magento_company_id.id,
#             'magento_currency_id': magento_settings.magento_currency_id.id,
#             'magento_journal_id': magento_settings.magento_journal_id.id,
#             'magento_sale_order_from_ecommerce': magento_settings.magento_sale_order_from_ecommerce,
#             'magento_licenze_key': magento_settings.magento_licenze_key,
#             'magento_website_ids': magento_website_ids,
#             'enable_multi_website': magento_settings.enable_multi_website,
#         }
#
#
#     @api.one
#     def set_settings_values(self):
#
#         magento_settings = self.env['magento.settings'].search([('id', '=', 1)])
#         if not magento_settings:
#             magento_settings = self.env['magento.settings'].create({})
#
#         company = self.env.user.company_id
#         company.name = self.company_name
#         magento_settings.url = self.magento_url
#         magento_settings.username = self.magento_ws_user
#         magento_settings.password = self.magento_psw_user
#         magento_settings.import_categories_interval_time = self.import_categories_interval_time
#         magento_settings.import_categories_interval_units = self.import_categories_interval_units
#         magento_settings.import_attributes_interval_time = self.import_attributes_interval_time
#         magento_settings.import_attributes_interval_units = self.import_attributes_interval_units
#         magento_settings.import_customers_interval_time = self.import_customers_interval_time
#         magento_settings.import_customers_interval_units = self.import_customers_interval_units
#         magento_settings.import_products_interval_time = self.import_products_interval_time
#         magento_settings.import_products_interval_units = self.import_products_interval_units
#         magento_settings.import_products_stock_interval_time = self.import_products_stock_interval_time
#         magento_settings.import_products_stock_interval_units = self.import_products_stock_interval_units
#         magento_settings.import_sales_orders_interval_time = self.import_sales_orders_interval_time
#         magento_settings.import_sales_orders_interval_units = self.import_sales_orders_interval_units
#         magento_settings.magento_sale_order_prefix = self.magento_sale_order_prefix
#         magento_settings.magento_sale_order_status = self.magento_sale_order_status
#         magento_settings.magento_customer_email = self.magento_customer_email
#         magento_settings.magento_product_simple_product = self.magento_product_simple_product
#         magento_settings.magento_sale_order_from = self.magento_sale_order_from
#         magento_settings.magento_sale_order_to = self.magento_sale_order_to
#         magento_settings.magento_sale_order_auto_invoice = self.magento_sale_order_auto_invoice
#         magento_settings.magento_invoice_prefix = self.magento_invoice_prefix
#         magento_settings.magento_account_id = self.magento_account_id
#         magento_settings.magento_company_id = self.magento_company_id
#         magento_settings.magento_currency_id = self.magento_currency_id
#         magento_settings.magento_journal_id = self.magento_journal_id
#         magento_settings.magento_sale_order_from_ecommerce = self.magento_sale_order_from_ecommerce
#         magento_settings.magento_licenze_key = self.magento_licenze_key
#         magento_settings.magento_website_ids = self.magento_website_ids
#         magento_settings.enable_multi_website = self.enable_multi_website
#
#     def create_cron_categories(self):
#         if self.import_categories_interval_time and self.import_categories_interval_units:
#             #Cerco se esiste gia'
#             exist = self.env['ir.cron'].search([('name', '=', 'magento_categories')])
#             vals = {
#                 'name': 'magento_categories',
#                 'interval_number': int(self.import_categories_interval_time),
#                 'interval_type': self.import_categories_interval_units,
#                 'model': 'magento.sync',
#                 'function': 'category_magento'
#             }
#             if not exist:
#                 #Lo creo
#                 self.env['ir.cron'].create(vals)
#             else:
#                 #Lo modifico
#                 exist.write(vals)
#         else:
#             raise osv.except_osv(('Error'), ('Insert interval number and unit'))
#
#     def create_cron_customers(self):
#         if self.import_categories_interval_time and self.import_categories_interval_units:
#             # Cerco se esiste gia'
#             exist = self.env['ir.cron'].search([('name', '=', 'magento_customers')])
#             vals = {
#                 'name': 'magento_customers',
#                 'interval_number': int(self.import_customers_interval_time),
#                 'interval_type': self.import_customers_interval_units,
#                 'model': 'magento.sync',
#                 'function': 'customer_magento'
#             }
#             if not exist:
#                 # Lo creo
#                 self.env['ir.cron'].create(vals)
#             else:
#                 # Lo modifico
#                 exist.write(vals)
#         else:
#             raise osv.except_osv(('Error'), ('Insert interval number and unit'))
#
#     def create_cron_attribute(self):
#         if self.import_categories_interval_time and self.import_categories_interval_units:
#             # Cerco se esiste gia'
#             exist = self.env['ir.cron'].search([('name', '=', 'magento_attribute')])
#             vals = {
#                 'name': 'magento_attribute',
#                 'interval_number': int(self.import_attributes_interval_time),
#                 'interval_type': self.import_attributes_interval_units,
#                 'model': 'magento.sync',
#                 'function': 'attribute_magento'
#             }
#             if not exist:
#                 # Lo creo
#                 self.env['ir.cron'].create(vals)
#             else:
#                 # Lo modifico
#                 exist.write(vals)
#         else:
#             raise osv.except_osv(('Error'), ('Insert interval number and unit'))
#
#     def create_cron_products(self):
#         if self.import_categories_interval_time and self.import_categories_interval_units:
#             # Cerco se esiste gia'
#             exist = self.env['ir.cron'].search([('name', '=', 'magento_product')])
#             vals = {
#                 'name': 'magento_product',
#                 'interval_number': int(self.import_products_interval_time),
#                 'interval_type': self.import_products_interval_units,
#                 'model': 'magento.sync',
#                 'function': 'product_magento'
#             }
#             if not exist:
#                 # Lo creo
#                 self.env['ir.cron'].create(vals)
#             else:
#                 # Lo modifico
#                 exist.write(vals)
#         else:
#             raise osv.except_osv(('Error'), ('Insert interval number and unit'))
#
#     def create_cron_products_stock(self):
#         if self.import_categories_interval_time and self.import_categories_interval_units:
#             # Cerco se esiste gia'
#             exist = self.env['ir.cron'].search([('name', '=', 'magento_stock')])
#             vals = {
#                 'name': 'magento_stock',
#                 'interval_number': int(self.import_products_stock_interval_time),
#                 'interval_type': self.import_products_stock_interval_units,
#                 'model': 'magento.sync',
#                 'function': 'stock_magento'
#             }
#             if not exist:
#                 # Lo creo
#                 self.env['ir.cron'].create(vals)
#             else:
#                 # Lo modifico
#                 exist.write(vals)
#         else:
#             raise osv.except_osv(('Error'), ('Insert interval number and unit'))
#
#     def create_cron_sales_orders(self):
#         if self.import_categories_interval_time and self.import_categories_interval_units:
#             # Cerco se esiste gia'
#             exist = self.env['ir.cron'].search([('name', '=', 'magento_sale_order')])
#             vals = {
#                 'name': 'magento_sale_order',
#                 'interval_number': int(self.import_sales_orders_interval_time),
#                 'interval_type': self.import_sales_orders_interval_units,
#                 'model': 'magento.sync',
#                 'function': 'sale_order_magento'
#             }
#             if not exist:
#                 # Lo creo
#                 self.env['ir.cron'].create(vals)
#             else:
#                 # Lo modifico
#                 exist.write(vals)
#         else:
#             raise osv.except_osv(('Error'), ('Insert interval number and unit'))