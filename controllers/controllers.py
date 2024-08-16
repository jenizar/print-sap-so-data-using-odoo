# -*- coding: utf-8 -*-
# from odoo import http


# class PrintDocument(http.Controller):
#     @http.route('/print_document/print_document', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/print_document/print_document/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('print_document.listing', {
#             'root': '/print_document/print_document',
#             'objects': http.request.env['print_document.print_document'].search([]),
#         })

#     @http.route('/print_document/print_document/objects/<model("print_document.print_document"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('print_document.object', {
#             'object': obj
#         })
