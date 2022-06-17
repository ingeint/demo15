# -*- coding: utf-8 -*-
# from odoo import http


# class L10nVeIgtf/(http.Controller):
#     @http.route('/l10n_ve_igtf//l10n_ve_igtf//', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_ve_igtf//l10n_ve_igtf//objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_ve_igtf/.listing', {
#             'root': '/l10n_ve_igtf//l10n_ve_igtf/',
#             'objects': http.request.env['l10n_ve_igtf/.l10n_ve_igtf/'].search([]),
#         })

#     @http.route('/l10n_ve_igtf//l10n_ve_igtf//objects/<model("l10n_ve_igtf/.l10n_ve_igtf/"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_ve_igtf/.object', {
#             'object': obj
#         })
