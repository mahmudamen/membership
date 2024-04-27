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
            this.report_options['filter_country'] = True;




            this.unfold();
            this.reload();
            this.load_more();
        },

    start: async function() {
        this.renderButtons();
        this.report_options['filter_country'] = True;

            this.reload();
            this.load_more();
            this.unfold();
        this.controlPanelProps.cp_content = {
            $buttons: this.$buttons,
            $searchview_buttons: this.$searchview_buttons,
            $pager: this.$pager,
            $searchview: this.$searchview,
        };
        await this._super(...arguments);
        this.render();
        this.reload();
        this.load_more();
        this.unfold();

        // A default value has been set for the filter accounts.
        // Apply the filter to take this value into account.
        if("default_filter_accounts" in (this.odoo_context || {}))
            this.$('.o_account_reports_filter_input').val(this.odoo_context.default_filter_accounts).trigger("input");
    },
    render_searchview_buttons: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.reload();
        this.load_more();
        this.unfold();





    },
    filter_accounts: function(e) {
        var self = this;
        var query = e.target.value.trim().toLowerCase();
        this.filterOn = false;
        this.reload();
            this.load_more();
        this.unfold();

        if (this.filterOn) {
            this.reload();
            this.load_more();
            this.unfold();
            this.$('.o_account_reports_level0.total').show();
            this.$('.o_account_reports_level1.total').show();

        }
        else {
            this.reload();
            this.load_more();
            this.unfold();
            this.$('.o_account_reports_level0.total').show();
            this.$('.o_account_reports_level1.total').show();


        }
        this.report_options['filter_accounts'] = query;
        this.render_footnotes();
        this.reload();
            this.load_more();
        this.unfold();
    },
     filter_country: function(e) {
        var self = this;
        this.report_options['filter_country'] = False;
            this.reload();
            this.load_more();
            this.unfold();
    },
    });

    return AccountReport;
});
