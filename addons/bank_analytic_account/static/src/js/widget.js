odoo.define('bank_analytic_account.analytic_account_id', function (require) {
"use strict";

var Widget = require('web.Widget');
var FieldManagerMixin = require('web.FieldManagerMixin');
var relational_fields = require('web.relational_fields');
var basic_fields = require('web.basic_fields');
var core = require('web.core');
var time = require('web.time');
var session = require('web.session');
var reconciliation_renderer= require('account.ReconciliationRenderer');
var reconciliation_model= require('account.ReconciliationModel');
var qweb = core.qweb;
var _t = core._t;

    reconciliation_renderer.LineRenderer.include({
        _makeAnalytic_account_idRecord: function (partnerID, partnerName) {
            var field = {
                relation: 'account.analytic.account',
                type: 'many2one',
                name: 'analytic_account_id',
            };
            if (partnerID) {
                field.value = [partnerID, partnerName];
            }
            return this.model.makeRecord('account.bank.statement.line', [field], {
                analytic_account_id: {}
            });
        },

        _renderCreate: function (state) {
            this._super(state);
            // analytic_account_id
            var self = this;
            self._makeAnalytic_account_idRecord(state.analytic_account_id, state.analytic_account_name).then(function (recordID) {
                self.fields.analytic_account_id.reset(self.model.get(recordID));
            });
        }
    });
    reconciliation_model.StatementModel.include({
        _formatToProcessReconciliation: function (line, prop) {
            var result = this._super(line, prop);
            if (prop.analytic_account_id){
                result.analytic_account_id = prop.analytic_account_id.id
            }else if(line.analytic_account_id){
                result.analytic_account_id = line.analytic_account_id;
            }
            return result;
        },
    });
});