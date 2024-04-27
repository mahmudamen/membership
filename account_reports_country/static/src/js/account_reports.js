odoo.define('account_reports_country.account_report_inherited', function (require) {
"use strict";

var core = require('web.core');
var Context = require('web.Context');
var AbstractAction = require('web.AbstractAction');
var Dialog = require('web.Dialog');
var datepicker = require('web.datepicker');
var session = require('web.session');
var field_utils = require('web.field_utils');
var RelationalFields = require('web.relational_fields');
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var { WarningDialog } = require("@web/legacy/js/_deprecated/crash_manager_warning_dialog");
var Widget = require('web.Widget');
var AccountReport = require('account_reports.account_report'); // Inherit from the base module
var QWeb = core.qweb;
var _t = core._t;

AccountReport = AbstractAction.extend({
        events: {
                'click .o_account_reports_load_more_partner': 'filter_country',

            },
    init: function () {
        this._super.apply(this, arguments);
            // Additional initialization logic for your new function
        },
    render_searchview_buttons: function() {
        var self = this;



        this.$searchview_buttons.find('.js_account_report_bool_filter').click(function (event) {
            var option_value = $(this).data('filter');
            self.report_options[option_value] = !self.report_options[option_value];
            if (option_value === 'unfold_all') {

            }

        });


    },
    unfold_all: function(bool) {
        var self = this;

        this.report_options['filter_unfold_all'] = True;
        var query = e.target.value.trim().toLowerCase();
        str.toLowerCase().startsWith(query);
        this.render();
        this.render_footnotes();
    },

     filter_country: function(e) {
        var self = this;
        this.report_options['filter_country'] = True;
        this.report_options['filter_unfold_all'] = True;
        var query = e.target.value.trim().toLowerCase();
        str.toLowerCase().startsWith(query);
        this.render();
        this.fold_unfold();
        this.render_footnotes();

    },
    });

    return AccountReport;
});
