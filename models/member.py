from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymMember(models.Model):
    _name = 'gym.member'
    _description = 'Flash Gym Member'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = 'name'

    name = fields.Char(
        required=True, tracking=True, string='Full Name',
    )

    member_code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('gym.member.seq'),
        readonly=True, copy=False,
    )
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(
        compute='_compute_age',
    )

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], required=True, tracking=True)
    phone = fields.Char(size=11)
    email = fields.Char()

    membership_state = fields.Selection([
        ('new', 'New'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('frozen', 'Frozen'),
        ('cancel', 'Cancelled'),
    ], default='new', string='Member Status', tracking=True)

    join_date = fields.Date(
        default=fields.Date.today,
    )

    notes = fields.Text(string='Notes')

    membership_ids = fields.One2many(
        'gym.membership',
        'member_id',
        string='Memberships',
    )
    #####################################
    # Statistical fields with its logic #
    #####################################

    total_paid_lifetime = fields.Float(
        help="Sum of all confirmed payments across all memberships for this member.",
        compute='_compute_financial_summary',
    )
    total_outstanding = fields.Float(
        help="Sum of all outstanding payments across all memberships for this member.",
        compute='_compute_financial_summary',
    )
    total_refunded = fields.Float(
        help="Sum of all refunded payments.",
        compute='_compute_financial_summary',
    )
    membership_count = fields.Integer(
        help="Total number of memberships (any state).",
        compute='_compute_financial_summary',
    )
    active_membership_id = fields.Many2one(
        'gym.membership',
        string='Active Membership',
        compute='_compute_active_membership',
    )

    @api.depends(
        'membership_ids.state',
        'membership_ids.payment_ids.state',
        'membership_ids.balance_due',
        'membership_ids.payment_ids.amount'
    )
    def _compute_financial_summary(self):
        for rec in self:
            all_payments = rec.membership_ids.mapped('payment_ids')

            confirmed = all_payments.filtered(
                lambda payment: payment.state == 'confirmed'
            )

            refunded = all_payments.filtered(
                lambda payment: payment.state == 'refunded'
            )
            active_membership = rec.membership_ids.filtered(
                lambda payment: payment.state in ('pending', 'active')
            )

            rec.total_paid_lifetime = sum(confirmed.mapped('amount'))
            rec.total_refunded = sum(refunded.mapped('amount'))
            rec.total_outstanding = sum(active_membership.mapped('balance_due'))
            rec.membership_count = len(rec.membership_ids)


    @api.depends('membership_ids.state')
    def _compute_active_membership(self):
        for rec in self:
            active = rec.membership_ids.filtered(
                lambda m: m.state == 'active'
            )
            rec.active_membership_id = active[:1]


    #####################
    # SQL Constraints   #
    #####################

    _sql_constraints = [
        (
            'unique_member_code',
            'UNIQUE (member_code)',
            "This code is used by another member"
        ),

        (
            'unique_phone',
            'UNIQUE (phone)',
            "Please enter your correct phone number."
            "This phone is used by another member"
        ),

        (
            'unique_email',
            'UNIQUE (email)',
            "Please enter your correct email address."
            "This email address is used by another member"
        ),
    ]




    #####################
    # Computed Methods  #
    #####################

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                rec.age = relativedelta(fields.Date.today(), rec.date_of_birth).years
            else:
                rec.age = 0


    def _compute_display_name(self):
        for rec in self:
            if rec.member_code:
                rec.display_name = f"[{rec.member_code}] {rec.name}"
            else:
                rec.display_name = rec.name or ''


    #####################
    # Constraints       #
    #####################

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email:
                if '@gmail.com' not in rec.email:
                    raise ValidationError(
                        "Email address must contain @gmai.com format."
                    )












