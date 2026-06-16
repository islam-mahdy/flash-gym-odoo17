from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymPayment(models.Model):
    _name = 'gym.payment'
    _description = 'Flash Gym Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payment_date desc'


    name = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('gym.payment.seq'),
        readonly=True, tracking=True, copy=False,
    )

    membership_id = fields.Many2one(
        'gym.membership', 'Membership',
        required=True, tracking=True
    )
    member_id = fields.Many2one(
        related='membership_id.member_id', store=True,
        string='Member'
    )

    amount = fields.Float(
        required=True, help="How much was paid this transaction?"
    )
    currency_id = fields.Many2one(
        related='membership_id.plan_id.currency_id',
        string='Currency',store=True,
    )

    payment_date = fields.Date(
        default=lambda self: fields.Date.today(), required=True,
    )
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online'),
    ], required=True, tracking=True)

    ref = fields.Char(
        string='External reference',
        help="bank transaction ID, card receipt number, etc."
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('refunded', 'Refunded'),
    ], default='draft')

    notes = fields.Char(string='Notes')


    #####################
    # Constraints       #
    #####################

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(
                    "Amount must be greater than 0"
                )
    @api.constrains('payment_date')
    def _check_payment_date(self):
        for rec in self:
            today = fields.Date.today()
            if rec.payment_date and rec.payment_date > today:
                raise ValidationError(
                    "Payment date cannot be in the future!"
                )

    #####################
    # Work Flows        #
    #####################

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(
                    "Can not confirm payment that is not in 'draft' state!"
                )
            rec.state = 'confirmed'
            rec.membership_id.amount_paid += rec.amount

    def action_refund(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise ValidationError(
                    "Can not refund payment that is not in 'confirmed' state!"
                )
            rec.state = 'refunded'
            rec.membership_id.amount_paid -= rec.amount





    #####################
    # Onchange Warning  #
    #####################


    #####################
    # Computed Methods  #
    #####################












