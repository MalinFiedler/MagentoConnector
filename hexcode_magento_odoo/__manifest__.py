{
    'name': 'Odoo Magento Connector',
    'version': '2.0',
    'category': 'all',
    'description': 'Magento odoo connector allows you to synchronize all the data on your magento ecommerce with odoo management. And it possible to import, export and update all your data.',
    'summary': 'Magento odoo connector. Import customers, quotations, sales orders, products, images and stock quantity. Update all your information. Export new contacts and products directly to your Magento Ecommerce. It synchronizes in real time and automatically all the data.',
    'author': 'hexcode',
    'website': 'www.hexcode.it',
    'support': 'federico@hexcode.it',
    'depends': [
        'base', 'product', 'sale', 'stock'
    ],
    'data': [
        'views/magento_odoo.xml',
        'views/product_product.xml',
        'views/import_widget.xml'
    ],
    'qweb': [
        'static/src/xml/multiwidget_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 749,
    'currency': 'EUR',
    'images': ['images/main_screenshot.png'],
}
