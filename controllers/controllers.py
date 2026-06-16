# -*- coding: utf-8 -*-
# from odoo import http


# class Flash(http.Controller):
#     @http.route('/flash/flash', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/flash/flash/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('flash.listing', {
#             'root': '/flash/flash',
#             'objects': http.request.env['flash.flash'].search([]),
#         })

#     @http.route('/flash/flash/objects/<model("flash.flash"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('flash.object', {
#             'object': obj
#         })

