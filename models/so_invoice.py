from odoo import api, fields, models
import requests
import json
from flask import Flask,render_template,request,redirect,url_for,flash
import sqlite3 as sql
import platform
import urllib.parse
from bs4 import BeautifulSoup
import datetime
from dateutil.relativedelta import relativedelta
app=Flask(__name__)
 
class So_Invoice(models.Model):
    _name = 'so.invoice'
    _description = 'Sales Order'    

    invoice_no = fields.Char(string='', readonly=True, default='/') 
    soid_line = fields.One2many('soid.line', 'soid_id', string='Sales Order Item')
    SALESORDERID = fields.Char(string='Sales Order ID')
    COMPANYNAME = fields.Char(string='Company Name')
    LEGALFORM = fields.Char(string='Legal Form')
    STREET = fields.Char(string='Street')
    BUILDING = fields.Char(string='Building')
    CITY = fields.Char(string='City')
    POSTALCODE = fields.Char(string='Postal Code')
    COUNTRY = fields.Char(string='Country')
    CURRENCYCODE = fields.Char(string='Currency')
    NETAMOUNT = fields.Char(string='Net Amount')
    TAXAMOUNT = fields.Char(string='Tax Amount')
    GROSSAMOUNT = fields.Char(string='Gross Amount')
    CHANGEDAT = fields.Char(string='Date')
    CUSTOMER = fields.Char(string='Customer')
    TOTALAMT = fields.Char(string='Total')
    V_URL = fields.Char(string='V_URL', default='http://vhcala4hci:50000/sap/bc/abap/zprint_so?sap-client=001&so_id=')
    P_URL = fields.Char(string='URL Parm')
    ADDRESS1 = fields.Char(string='Address 1')
    ADDRESS2 = fields.Char(string='Address 2')
    DATFLOAT = fields.Float(string='Float Var')
    EXPIREDAT = fields.Char(string='Expiration')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')], string='Status', readonly=True, default='draft')

    @api.model
    def create(self, vals):
        vals['invoice_no'] = self.env['ir.sequence'].next_by_code('so.invoice')
        return super(So_Invoice, self).create(vals)

    def get_so(self):
        self.write({'state': 'open'})  
        for record in self:      
            record.P_URL = f"{record.V_URL or ''} {record.SALESORDERID or ''}".strip()
        record.P_URL = record.P_URL.replace(" ", "")  
        username = 'DEVELOPER'
        password = 'ABAPtr1909'
        response = requests.get(self.P_URL, auth=(username, password)).content
        soup = BeautifulSoup(response, 'html.parser')
        for tag in soup.find_all('body'):
            json_head = json.loads(tag.text)
            json_res = json.loads(tag.text)
        for head_data in json_head:
            self.CUSTOMER = (head_data['COMPANYNAME'] + ", " + head_data['LEGALFORM'])
            self.ADDRESS1 = (head_data['STREET'] + " " + head_data['BUILDING'])                 
            self.ADDRESS2 = (head_data['CITY'] + " " + head_data['POSTALCODE'] + ", " + head_data['COUNTRY'])
            self.DATFLOAT = head_data['CHANGEDAT']
            self.CHANGEDAT = str(self.DATFLOAT)
            self.CURRENCYCODE = head_data['CURRENCYCODE']
            self.GROSSAMOUNT = head_data['GROSSAMOUNT']
            self.TOTALAMT = head_data['GROSSAMOUNT']
        self.CHANGEDAT = self.CHANGEDAT[6:8] + '/' + self.CHANGEDAT[4:6] + '/' + self.CHANGEDAT[0:4]
        one_year_from_now = datetime.datetime.now() #+ relativedelta(years=1)
        date_formated = one_year_from_now.strftime("%d/%m/%Y")
        self.EXPIREDAT = date_formated
        #self.EXPIREDAT = datetime.today().strftime('%Y-%m-%d')

        rplace = []
        for item in json_res:           
            val = {'PRODUCTNAME' : item["PRODUCTNAME"],
                  'MEASUREUNIT' : item["MEASUREUNIT"],
                  'ITEMNETAMOUNT' : item["ITEMNETAMOUNT"],
                  'ITEMTAXAMOUNT' : item["ITEMTAXAMOUNT"] ,
                  'SUB_TOTAL' : item["ITEMGROSSAMOUNT"]}    
            rplace.append((0,0,val))          
        self.soid_line = rplace 

    def action_print_session(self):
        return self.env.ref('print_document.report_print_so_action').report_action(self)   
      
    def action_cancel(self):
        self.write({'state': 'draft'})
      
    def action_close(self):
        self.write({'state': 'done'})
      
    def action_cancel(self):
        self.write({'state': 'draft'})
      
    def action_close(self):
        self.write({'state': 'done'})


class soid_line(models.Model):
    _name = 'soid.line'
    _description = 'Sales Order Item'

    soid_id = fields.Many2one('so.invoice', string='Sales Order ID')
    PRODUCTNAME = fields.Char(string='Product Name')
    MEASUREUNIT = fields.Char(string='Unit')
    ITEMNETAMOUNT = fields.Char(string='Amount')
    ITEMTAXAMOUNT = fields.Char(string='Tax')
    ITEMGROSSAMOUNT = fields.Char(string='Total')
    SUB_TOTAL = fields.Float(string='Sub Total')