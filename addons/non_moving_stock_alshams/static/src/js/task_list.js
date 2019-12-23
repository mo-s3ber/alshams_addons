openerp.project = function (instance){
    var QWeb = openerp.web.qweb;
    _t = instance.web._t;
    var self = this;
openerp.web.ListView.include({
    load_list: function(data) {
        this._super(data);
        if (this.$buttons) {
            this.$buttons.find('.oe_new_button').off().click(this.proxy('do_the_job')) ;
            console.log('Save & Close button method call...');
        }
    },
    do_the_job: function () {
        this.do_action({
            type: "ir.actions.act_window",
            name: "Stock move line",
            res_model: "stock.move.line",
            views: [[false,'form']],
            target: 'current',
            view_type : 'form',
            view_mode : 'form',
            flags: {'form': {'action_buttons': true, 'options': {'mode': 'edit'}}}
        });
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
        }
}
});
}