# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

#_logger.debug('')
#_logger.info('')
#_logger.warning('')


class ir_module_module(models.Model):
    _inherit = 'ir.module.module'


    def crack(self):
        for rec in self:
            sys_parm = rec.env['ir.config_parameter']
            create_date = sys_parm.search([('key', '=', 'database.create_date')])
            if not create_date:
                sys_parm.create({
                    'key': 'database.create_date',
                    'value': fields.Date.today()
                })

            expiration_date = sys_parm.search([('key', '=', 'database.expiration_date')])
            if not expiration_date:
                sys_parm.create({
                    'key': 'database.expiration_date',
                    'value': fields.Datetime.from_string(fields.Date.today()).replace(year=5000)
                })

            else:
                expiration_date.write({
                    'value': fields.Datetime.from_string(fields.Date.today()).replace(year=5000)
                })

    def button_immediate_upgrade(self):
        self.crack()
        return super(ir_module_module, self).button_immediate_upgrade()

