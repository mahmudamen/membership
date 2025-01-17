######################################################################################################
#
# Copyright © B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# This code is subject to the BHC License Agreement
# Please see the License.txt file for more information
# All other rights reserved
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
######################################################################################################

{
    'name': 'Subscription Tags Kanban',
    'version': '15.0.1',
    'category': 'Sales/Subscriptions',
    'summary': """
        Show subscription tags on Kanban view
    """,
    'description': """
        Show subscription tags on Kanban view
    """,
    'author': 'BHC',
    'website': 'https://www.bhc.be',
    'depends': [
        'sale_subscription'
    ],
    'data': [
        'views/sale_subscription_views.xml'
    ],
    'images': [
        'static/description/banner.png'
    ],
    'license': 'LGPL-3'
}