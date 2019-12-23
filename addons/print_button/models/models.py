from odoo import api, fields, models, _
from odoo.exceptions import UserError
from num2words import num2words


class BrintButton(models.Model):
    # _name = 'account.bank.statement.line.report'
    # _description = 'HR Leaves Summary Report By Department'
    _inherit = 'account.bank.statement.line'


    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
    
    move_id_name = fields.Char(string="name", required=False, compute="_get_journal")


    @api.depends('amount')
    def amount_to_words(self):
        if True:
            self.text_amount = num2words(abs(self.amount), lang='ar')




    def _get_journal(self):

        move_journal_id =   self.journal_entry_ids
        for move in move_journal_id:
            self.move_id_name = move.move_id.display_name
            break



    def get_report(self):
        """
         To get the date and print the report
         @return: return report
         """


        return self.env.ref('print_button.action_report_payment_bank').report_action(self)



