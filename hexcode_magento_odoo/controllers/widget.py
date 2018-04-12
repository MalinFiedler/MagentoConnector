from odoo import models,api,fields

class widget_data(models.Model):
    _inherit = 'ir.attachment'

    extension = fields.Char()
    sortable = fields.Integer()

    @api.model
    def upload_dragndrop(self, name, base64, extension, sortable):
        Model = self
        try:
            attachment_id = Model.create({
                'name': name,
                'datas': base64,
                'extension': extension,
                'datas_fname': name,
                'res_model': Model._name,
                'description': '',
                'sortable': sortable,
                'res_id': 0
            })
            args = {
                'filename': name,
                'id':  attachment_id
            }
        except Exception:
            args = {'error': "Something horrible happened"}
        # return out % (simplejson.dumps(callback), simplejson.dumps(args))
        return attachment_id.id

    @api.model
    def attachment_update_description(self, id, description):
        attachment_id = self.env['ir.attachment'].search([('id', '=', int(id))])[0]
        attachment_id.description = description

    @api.model
    def update_sort_attachment(self, attachments_ids):
        attachments = self.env['ir.attachment'].search([('id', 'in', attachments_ids)])
        for attach in attachments:
            #cambio il campo sortable
            sort_number = attachments_ids.index(str(attach.id))
            attach.sortable = sort_number


class widget_ir_config_parameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_base_url(self):
        base_url = ""
        config_parameter_ids = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')])[0]
        if config_parameter_ids.value:
            base_url = config_parameter_ids.value
        return base_url

widget_data()
widget_ir_config_parameter()