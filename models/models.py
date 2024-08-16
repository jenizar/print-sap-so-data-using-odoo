# -*- coding: utf-8 -*-

from odoo import api, fields, models
 
class PrintDocument(models.Model):
    _name = 'print.document'
    _description = 'Print Document'
     
    name = fields.Char(string='Print Document', required=True)
    description = fields.Text(string='Description')