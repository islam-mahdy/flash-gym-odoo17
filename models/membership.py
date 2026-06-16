from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymMembership(models.Model):
    _name = 'gym.membership'
    _description = 'Flash Gym Membership'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'


    member_id = fields.Many2one(
        'gym.member', 'Member', required=True,tracking=True
    )
    plan_id = fields.Many2one(
        'gym.subscription.plan', 'Subscription Plan', required=True,tracking=True
    )

    start_date = fields.Date(
        default=fields.Date.today,
        string='Start Date', required=True,
        )
    end_date = fields.Date(
        string='End Date',
        compute='_compute_end_date',
        store=True,
    )

    state = fields.Selection([
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('frozen', 'Frozen'),
        ('cancel', 'Cancelled'),
    ], default='pending', string='Status', tracking=True)

    total_price = fields.Float(
        related='plan_id.price'
    )
    amount_paid = fields.Float(
        string='Amount Paid', digits=(10, 2),
        tracking=True
    )
    balance_due = fields.Float(
        string='Balance Due',digits=(10, 2),
        compute='_compute_balance_due', store=True
    )

    notes = fields.Text(string='Notes')

    freeze_start_date = fields.Date(
        string='Freeze Start Date', readonly=True,
    )

    total_frozen_days = fields.Integer(readonly=True)
        # compute='_compute_total_frozen_days',

    cancelled_reason = fields.Char('Cancellation Reason')

    payment_ids = fields.One2many(
        'gym.payment', 'membership_id',
        string="Payments"
    )
    payment_count = fields.Integer(
        'Payment Count', compute="_compute_payment_count",
    )

    #####################
    # Work Flows        #
    #####################

    def action_active(self):
        for rec in self:
            if rec.state == 'pending':
                rec.state = 'active'
                rec.member_id.membership_state = 'active'
                rec.freeze_start_date = False
            else:
                raise ValidationError(
                    f"You can not move from {rec.state} to active directly"
                )

    def action_frozen(self):
        for rec in self:
            if rec.state == 'active':
                plan = rec.plan_id
                if plan.max_freeze_days == 0:
                    raise ValidationError(
                        f"The plan '{plan.name}' does not allow freezing."
                    )

                if rec.total_frozen_days >= plan.max_freeze_days:
                    raise ValidationError(
                        f"This membership has used all {plan.max_freeze_days} "
                        f"allowed freeze days."
                    )

                rec.state = 'frozen'
                rec.freeze_start_date = fields.Date.today()
                rec.member_id.membership_state = 'frozen'

            else:
                raise ValidationError(
                    f"You can not move from {rec.state} to frozen directly"
                )

    def action_unfreeze(self):
        for rec in self:
            if rec.state != 'frozen':
                raise ValidationError("Only frozen memberships can be unfrozen.")

            if rec.freeze_start_date:
                frozen_days = (fields.Date.today() - rec.freeze_start_date).days
                rec.total_frozen_days += frozen_days

            if rec.end_date:
                rec.end_date = rec.end_date + timedelta(days=frozen_days)
                
            rec.freeze_start_date = False

            rec.state = 'active'
            rec.member_id.membership_state = 'active'


    def action_cancelled(self):
        for rec in self:
            if rec.state in ('active', 'pending'):
                rec.state = 'cancel'

                other_active = self.search([
                    ('member_id', '=', rec.member_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', rec.id)
                ])
                if not other_active:
                    rec.member_id.membership_state = 'cancel'

            else:
                raise ValidationError(
                    f"You can not move from {rec.state} to cancelled directly"
                )



    #####################
    # Wizard Actions    #
    #####################
    def action_open_payment_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Wizard',
            'res_model': 'gym.payment.wizard',
            'view_mode': 'form',
            'context': {
                'default_membership_id': self.id,
                'default_amount': self.balance_due,
            },
            'target': 'new',
        }

    #####################
    # Onchange Trigger  #
    #####################

    @api.onchange('plan_id')
    def _onchange_plan_id(self):
        if self.plan_id and self.start_date:
            self.end_date = self.start_date + relativedelta(
                days=self.plan_id.duration_days
            )
        if self.plan_id and self.plan_id.max_freeze_days == 0:
            return {
                'warning': {
                    'title': 'No Freeze Allowed',
                    'message': f"The plan '{self.plan_id.name}' does not "
                               f"allow membership freezing.",
                }
            }

    @api.onchange('member_id')
    def _onchange_member_id(self):
        if not self.start_date:
            self.start_date = fields.Date.today()
        if self.member_id:
            existing = self.env['gym.membership'].search([
                ('member_id', '=', self.member_id.id),
                ('state', 'in', ('active', 'pending')),
            ])
            if existing:
                return {
                    'warning': {
                        'title': 'Existing Membership',
                        'message': f"'{self.member_id.name}' already has an "
                                   f"active or pending membership.",
                    }
                }

    #####################
    # Computed Methods  #
    #####################

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)

    @api.depends('start_date', 'plan_id.duration_days')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date and rec.plan_id.duration_days:
                duration_days = rec.plan_id.duration_days
                rec.end_date = rec.start_date + relativedelta(days=duration_days)
            else:
                rec.end_date = False


    @api.depends('plan_id.price', 'amount_paid')
    def _compute_balance_due(self):
        for rec in self:
            if rec.plan_id.price:
                rec.balance_due = rec.total_price - rec.amount_paid


    def _compute_display_name(self):
        for rec in self:
            if rec.member_id and rec.plan_id:
                if rec.end_date:
                    rec.display_name = (f"[{rec.member_id.name}] - {rec.plan_id.name}"
                                        f" {rec.start_date:%Y-%m-%d %H:%M:%S} → {rec.end_date:%Y-%m-%d %H:%M:%S}")
                else:
                    rec.display_name = f"[{rec.member_id.name}] - {rec.plan_id.name} ? → ?"
            else:
                rec.display_name = "New Membership"

    #####################
    # Constraints       #
    #####################

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.end_date and rec.start_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError(
                        "The end date must be after start date."
                    )

    @api.constrains('amount_paid')
    def _check_amount_paid(self):
        for rec in self:
            if rec.amount_paid:
                if rec.amount_paid < 0:
                    raise ValidationError(
                        "The amount paid cannot be negative."
                    )

    @api.constrains( 'member_id', 'state')
    def _check_duplicated_active_plans(self):
        for rec in self:
            if rec.state in ['active', 'pending']:
                plans = self.search([
                    ('member_id', '=', rec.member_id.id),
                    ('state', 'in', ('active', 'pending')),
                    ('id', '!=', rec.id),
                ])
                if plans:
                    raise ValidationError(
                        f"Member '{rec.member_id.name}' already has an "
                        f"active or pending membership."
                    )

    #######################
    # Cron Jobs           #
    #######################

    def action_check_expired_date(self):
        today = fields.Date.today()

        expired = self.search([
            ('state', 'in', 'active'),
            ('end_date', '<', today),
        ])
        for membership in expired:
            membership.state = 'expired'

            other_active = self.search([
                ('member_id', '=', membership.member_id.id),
                ('state', '=', 'active'),
            ])
            if not other_active:
                membership.member_id.membership_state = 'expired'













