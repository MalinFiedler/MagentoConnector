

from odoo import fields, models, api
#import sys
#reload(sys)
#sys.setdefaultencoding("utf8")


class StockMoveMagento(models.Model):
    _inherit = 'stock.move'

    weight_uom_id = fields.Many2one('product.uom', string='Weight Unit of Measure', required=False, readonly=True,
                                    help="Unit of Measure (Unit of Measure) is the unit of measurement for Weight")


class multi_magento_store(models.Model):
    _name = 'multi.magento.website'

    #Magento Website Name
    name = fields.Char()
    url = fields.Char(String="Url Magento")
    username = fields.Char(String="Web Service Username")
    password = fields.Char(String="Web Service Password")

class magento_odoo(models.Model):
    _name = 'magento.odoo'

    id = fields.Integer()

class magento_store(models.Model):
    _name = 'magento.store'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Integer()
    store_id = fields.Integer()
    code = fields.Char()
    website_id = fields.Integer()
    group_id = fields.Integer()
    name = fields.Char()
    sort_order = fields.Integer()
    is_active = fields.Boolean()


class magento_category(models.Model):
    _inherit = 'product.category'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Integer()
    store_id = fields.Integer()
    store_name = fields.Char()

class magento_product_type(models.Model):
    _name = 'magento.product.type'

    magento_website_id = fields.Many2one('multi.magento.website')
    type = fields.Char()
    label = fields.Char()
    name = fields.Char()

class magento_product(models.Model):
    _inherit = 'product.product'

    # magento_website_id = fields.Many2many('multi.magento.website')
    magento_website_ids = fields.Many2many('magento.website.rel')
    magento_id = fields.Integer()

    def export_update_stock(self):
        # Connect to WS Magento
        socket, session = self.env['magento.sync'].connection()
        # Prendo tutti i prodotti magento
        product_ids = self

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
            parameter.append(self.env['magento.sync'].random(10))
            id = socket.call(session, "catalog_product.update", parameter)

    def export_update_product(self):
        # Connect to WS Magento
        socket, session = self.env['magento.sync'].connection()
        # Prendo tutti i prodotti magento
        product_ids = self
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

            if product.magento_status:
                datas['status'] = str('1')
            else:
                datas['status'] = str('2')

            datas['visibility'] = str(product.magento_visibility)
            if product.magento_special_price:
                datas['special_price'] = product['magento_special_price']
            if product.magento_special_from_date:
                datas['special_from_date'] = str(product.magento_special_from_date)
            if product.magento_special_to_date:
                datas['special_to_date'] = str(product.magento_special_to_date)
            if product.magento_meta_title:
                datas['meta_title'] = str(product.magento_meta_title)
            if product.magento_meta_keyword:
                datas['meta_keyword'] = str(product.magento_meta_keyword)
            if product.magento_meta_description:
                datas['meta_description'] = str(product.magento_meta_description)
            if product.magento_custom_design:
                datas['custom_design'] = str(product.magento_custom_design)
            if product.name:
                datas['name'] = str(product.name)
            if product.list_price:
                datas['price'] = str(product.list_price)
            if product.description_sale:
                datas['description'] = str(product.description_sale)

            category_ids = []
            for category in product.magento_category_ids:
                if category.magento_id:
                    category_ids.append(str(category.magento_id))
            if len(category_ids) > 0:
                datas['category_ids'] = category_ids

            parameter.append(str(product.magento_id))
            parameter.append(datas)
            parameter.append('1')
            parameter.append('dkslwodlxz')
            id = socket.call(session, "catalog_product.update", parameter)



class magento_customers_group(models.Model):
    _name = 'magento.customers.group'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_group_id = fields.Integer()
    magento_group_code = fields.Char()
    name = fields.Char()

class magento_tier_price(models.Model):
    _name = 'magento.tier.price'

    magento_website_id = fields.Many2one('multi.magento.website')
    id = fields.Integer()
    customer_group = fields.Many2one('magento.customers.group')
    website = fields.Char()
    qty = fields.Float()
    cost = fields.Float()
    product_id = fields.Many2one('product.product')

class magento_product_template(models.Model):
    _inherit = 'product.template'

    # magento_website_id = fields.Many2one('multi.magento.website')
    magento_website_ids = fields.Many2many('magento.website.rel')
    magento_images_ids = fields.Many2many('ir.attachment')
    magento_status = fields.Boolean()
    magento_weight = fields.Char()
    magento_special_price = fields.Float()
    magento_visibility = fields.Boolean()
    magento_set = fields.Many2one('magento.attribute.set')
    magento_type = fields.Many2one('magento.product.type')
    magento_category_ids = fields.Many2many('product.category')
    magento_special_from_date = fields.Date()
    magento_special_to_date = fields.Date()
    magento_meta_title = fields.Char()
    magento_meta_keyword = fields.Char()
    magento_meta_description = fields.Text()
    magento_custom_design = fields.Char()
    magento_tier_price = fields.One2many('magento.tier.price', 'product_id')



    def export_update_stock(self):
        # Connect to WS Magento
        socket, session = self.env['magento.sync'].connection()
        # Prendo tutti i prodotti magento
        product_ids = self.env['product.product'].search([('product_tmpl_id', '=', int(self.id))])

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
            parameter.append(self.env['magento.sync'].random(10))
            id = socket.call(session, "catalog_product.update", parameter)

    def export_update_product(self):
        # Connect to WS Magento
        socket, session = self.env['magento.sync'].connection()
        # Prendo tutti i prodotti magento
        product_ids = self.env['product.product'].search([('product_tmpl_id', '=', int(self.id))])
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

            if product.magento_status:
                datas['status'] = str('1')
            else:
                datas['status'] = str('2')
            datas['visibility'] = str(product.magento_visibility)
            if product.magento_special_price:
                datas['special_price'] = product['magento_special_price']
            if product.magento_special_from_date:
                datas['special_from_date'] = str(product.magento_special_from_date)
            if product.magento_special_to_date:
                datas['special_to_date'] = str(product.magento_special_to_date)
            if product.magento_meta_title:
                datas['meta_title'] = str(product.magento_meta_title)
            if product.magento_meta_keyword:
                datas['meta_keyword'] = str(product.magento_meta_keyword)
            if product.magento_meta_description:
                datas['meta_description'] = str(product.magento_meta_description)
            if product.magento_custom_design:
                datas['custom_design'] = str(product.magento_custom_design)
            if product.name:
                datas['name'] = str(product.name)
            if product.list_price:
                datas['price'] = str(product.list_price)
            if product.description_sale:
                datas['description'] = str(product.description_sale)

            category_ids = []
            for category in product.magento_category_ids:
                if category.magento_id:
                    category_ids.append(str(category.magento_id))
            if len(category_ids) > 0:
                datas['category_ids'] = category_ids

            parameter.append(str(product.magento_id))
            parameter.append(datas)
            parameter.append('1')
            parameter.append('opkjbnmjhg')
            id = socket.call(session, "catalog_product.update", parameter)



class magento_attributes_set(models.Model):
    _name = 'magento.attribute.set'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Integer()
    name = fields.Char()
    attributes_ids = fields.Many2many(comodel_name='product.attribute',
                                relation='attribute_set_attribute_rel',
                                column1='set_id',
                                column2='attribute_id')

class magento_attribute(models.Model):
    _inherit = 'product.attribute'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Integer()
    attribute_set_ids = fields.Many2many(comodel_name='magento.attribute.set',
                                      relation='attribute_set_attribute_rel',
                                      column1='attribute_id',
                                      column2='set_id')
    magento_default_value = fields.Char()
    magento_is_unique = fields.Boolean()
    magento_is_required = fields.Boolean()
    magento_is_configurable = fields.Boolean()
    magento_is_searchable = fields.Boolean()
    magento_is_visible_in_advanced_search = fields.Boolean()
    magento_is_comparable = fields.Boolean()
    magento_is_used_for_promo_rules = fields.Boolean()
    magento_is_visible_on_front = fields.Boolean()
    magento_used_in_product_listing = fields.Boolean()


class magento_attribute_value(models.Model):
    _inherit = 'product.attribute.value'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Integer()


class magento_website_rel(models.Model):
    _name = 'magento.website.rel'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Integer()

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[' + str(record.magento_website_id.url) + ']'
            result.append((record.id, name))
        return result

class magento_customer(models.Model):
    _inherit = 'res.partner'

    # magento_website_id = fields.Many2many('multi.magento.website')
    magento_website_ids = fields.Many2many('magento.website.rel')
    magento_id = fields.Integer()
    magento_group = fields.Many2one('magento.customers.group')
    store_id = fields.Many2one('magento.store')
    website_id = fields.Integer()
    mfirstname = fields.Char()
    mlastname = fields.Char()
    mpassword = fields.Char()
    mgender = fields.Selection(selection=[(1, 'Male'), (2, 'Female'), ])
    mmiddlename = fields.Char()


    def export_single_customer(self):
        # Connect to WS Magento
        socket, session = self.env['magento.sync'].connection()
        vals = {}
        if self.id:
            customer = self
            if customer.email:
                vals['email'] = customer.email
            magento_settings = self.env['magento.sync'].getSettings()
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
                print('errore esportazione')

class magento_region(models.Model):
    _inherit = 'res.country.state'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Char()

class magento_state(models.Model):
    _inherit = 'res.country'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Char()

class magento_sale_order(models.Model):
    _inherit = 'sale.order'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Char()
    magento_comment = fields.Text()


class magento_ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Boolean()

class magento_invoice(models.Model):
    _inherit = 'account.invoice'

    magento_website_id = fields.Many2one('multi.magento.website')
    magento_id = fields.Char()

