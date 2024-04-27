# -*- coding: utf-8 -*-
######################################################################################################
#
# Copyright (C) B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
######################################################################################################
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    blacklist = fields.Boolean(string='Blacklist')

    @api.onchange('category_id')
    def onchange_category_id(self):
        self.blacklist = any(partner_categ.blacklist for partner_categ in self.category_id)
        self.sale_warn = 'block' if self.blacklist else 'no-message'
        self.sale_warn_msg = "Blacklisted Partner" if self.sale_warn != 'no-message' and not self.sale_warn_msg else self.sale_warn_msg


class ResPartnerCategory(models.Model):
    _inherit = "res.partner.category"

    blacklist = fields.Boolean(string='Blacklist')