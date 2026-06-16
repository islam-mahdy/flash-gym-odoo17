from odoo import fields, models
from odoo.exceptions import ValidationError


class GymPaymentWizard(models.TransientModel):
    _name = 'gym.payment.wizard'
    _description = 'Gym Payment Wizard'


    membership_id = fields.Many2one(
        'gym.membership', 'Membership',
        readonly=True
    )
    member_id = fields.Many2one(
        related='membership_id.member_id', string='Member'
    )
    amount = fields.Float()
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online'),
    ], required=True, default='cash')

    ref = fields.Char()
    balance_due = fields.Float(
        related='membership_id.balance_due'
    )
    notes = fields.Text()

    def action_record_payment(self):
        self.ensure_one()
        if self.amount <= 0:
            raise ValidationError(
                'Amount must be greater than 0'
            )
        payment = self.env['gym.payment'].create({
            'membership_id': self.membership_id.id,
            'amount': self.amount,
            'ref': self.ref,
            'state': 'confirmed',
            'payment_method': self.payment_method,
            'payment_date': fields.Date.today(),
        })
        self.membership_id.amount_paid += self.amount

