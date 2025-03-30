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

class Po_Invoice(models.Model):
    _name = 'po.invoice'
    _description = 'Purchase Order'       

    invoice_no = fields.Char(string='', readonly=True, default='/') 
    poid_line = fields.One2many('poid.line', 'poid_id', string='Purchase Order Item')
    PONUMBER = fields.Char(string='Purchase Order Number')
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
    TERMS = fields.Char(string='Terms')
    V_URL = fields.Char(string='V_URL', default='http://vhcala4hci:50000/sap/bc/abap/zprint_po?sap-client=001&po_id=')
    P_URL = fields.Char(string='URL Parm')    
    ADDRESS1 = fields.Char(string='Address 1')
    ADDRESS2 = fields.Char(string='Address 2')
    DATFLOAT = fields.Float(string='Float Var')
    CREATEDAT = fields.Char(string='Date of created')
    OVERALLSTATUS = fields.Char(string='Overall Status')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')], string='Status', readonly=True, default='draft')

    @api.model
    def create(self, vals):
        vals['invoice_no'] = self.env['ir.sequence'].next_by_code('po.invoice')
        return super(Po_Invoice, self).create(vals)
    
    def get_po(self):
        self.write({'state': 'open'})  
        for record in self:      
            record.P_URL = f"{record.V_URL or ''} {record.PONUMBER or ''}".strip()
        record.P_URL = record.P_URL.replace(" ", "")  
        username = 'DEVELOPER'
        password = 'ABAPtr2022#01'
        response = requests.get(self.P_URL, auth=(username, password)).content        
        soup = BeautifulSoup(response, 'html.parser')        
        for tag in soup.find_all('body'):
            json_head = json.loads(tag.text)            
            json_res = json.loads(tag.text)
        for head_data in json_head:
            self.CUSTOMER = (head_data['COMPANYNAME'] + ", " + head_data['LEGALFORM'])
            self.ADDRESS1 = (head_data['STREET'] + " " + head_data['BUILDING'])                 
            self.ADDRESS2 = (head_data['CITY'] + " " + head_data['POSTALCODE'] + ", " + head_data['COUNTRY'])
            self.DATFLOAT = head_data['CREATEDAT']
            self.CREATEDAT = str(self.DATFLOAT)
            self.CURRENCYCODE = head_data['CURRENCYCODE']
            self.GROSSAMOUNT = head_data['GROSSAMOUNT']
            self.TOTALAMT = head_data['GROSSAMOUNT']            
            if (head_data['OVERALLSTATUS'] == 'P'):
                self.OVERALLSTATUS = 'Awaiting Approval'
            elif (head_data['OVERALLSTATUS'] == 'A'):
                self.OVERALLSTATUS = 'Approved'
            elif (head_data['OVERALLSTATUS'] == 'R'):
                self.OVERALLSTATUS = 'Rejected by Approver'
            elif (head_data['OVERALLSTATUS'] == 'S'):
                self.OVERALLSTATUS = 'Sent'                                
            elif (head_data['OVERALLSTATUS'] == 'F'):
                self.OVERALLSTATUS = 'Confirmed'     
            elif (head_data['OVERALLSTATUS'] == 'D'):
                self.OVERALLSTATUS = 'Delivered'
            elif (head_data['OVERALLSTATUS'] == 'I'):
                self.OVERALLSTATUS = 'Invoiced'
            elif (head_data['OVERALLSTATUS'] == 'X'):
                self.OVERALLSTATUS = 'Cancelled'
            elif (head_data['OVERALLSTATUS'] == 'J'):
                self.OVERALLSTATUS = 'Rejected by Supplier'
            else:
                self.OVERALLSTATUS = 'Completed'
        print('-------------------------------------------')                
        print('HEADER:', json_head)              
        print('-------------------------------------------')                                                                            
        self.CREATEDAT = self.CREATEDAT[6:8] + '/' + self.CREATEDAT[4:6] + '/' + self.CREATEDAT[0:4]
        rplace = []
        for item in json_res:           
            val = {'PRODUCTNAME' : item["PRODUCTNAME"],
                   'MEASUREUNIT' : item["MEASUREUNIT"],
                  'ITEMNETAMOUNT' : item["ITEMNETAMOUNT"],
                  'ITEMTAXAMOUNT' : item["ITEMTAXAMOUNT"] ,
                  'SUB_TOTAL' : item["ITEMGROSSAMOUNT"]}    
            rplace.append((0,0,val))    
            print('DETAIL:', json_res)          
        self.poid_line = rplace 

    def action_print_session(self):
        return self.env.ref('print_document.report_print_po_action').report_action(self)   
      
    def action_cancel(self):
        self.write({'state': 'draft'})
      
    def action_close(self):
        self.write({'state': 'done'})
      
    def action_cancel(self):
        self.write({'state': 'draft'})
      
    def action_close(self):
        self.write({'state': 'done'})


class poid_line(models.Model):
    _name = 'poid.line'
    _description = 'Purchase Order Item' 

    poid_id = fields.Many2one('po.invoice', string='Purchase Order Number')
    PRODUCTNAME = fields.Char(string='Product Name')
    MEASUREUNIT = fields.Char(string='Unit')    
    ITEMNETAMOUNT = fields.Char(string='Amount')
    ITEMTAXAMOUNT = fields.Char(string='Tax')
    ITEMGROSSAMOUNT = fields.Char(string='Total')
    SUB_TOTAL = fields.Float(string='Sub Total')  