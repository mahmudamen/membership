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
{
    'name': 'Blacklist Partner',
    'version': '13.0',
    'category': 'Generic Modules/Others',
    'author': 'BHC',
    'website': 'www.bhc.be',
    'depends': ['base', 'sale', 'contacts'],
    'images': ['static/description/banner.png'],
    'data': [
        'data/blacklist_data.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}