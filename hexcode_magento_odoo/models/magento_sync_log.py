from odoo import models,api,fields


class magento_sync_log(models.Model):
    _name = 'magento.sync.log'

    log = fields.Html()