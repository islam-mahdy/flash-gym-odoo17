from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymSubscriptionPlan(models.Model):
    _name = 'gym.subscription.plan'
    _description = 'Flash GYM Subscription Plan'
    _order = 'price desc'

    name = fields.Char(
        required=True, string='Plan Name',
    )

    plan_code = fields.Char(required=True, copy=False)
        # default=lambda self: self.env['ir.sequence'].next_by_code('gym.member.seq'),
        # readonly=True, copy=False,)

    duration_days = fields.Integer(
        required=True, string='Duration (Days)'
    )

    price = fields.Float(digits=(10, 2), tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    max_freeze_days = fields.Integer(
        string='Max Freeze Days/Year', default=0
    )

    includes_pool = fields.Boolean()
    includes_classes = fields.Boolean(string='Includes Group Classes')
    includes_personal_training = fields.Boolean()

    active = fields.Boolean(default=True)

    description = fields.Text(string='Description')



    #####################
    # SQL Constraints   #
    #####################

    _sql_constraints = [
        (
            'unique_plan_code',
            'UNIQUE (plan_code)',
            "A subscription plan with this code already exists!"
        ),

    ]




    #####################
    # Computed Methods  #
    #####################



    def _compute_display_name(self):
        for rec in self:
            if rec.plan_code:
                rec.display_name = f"[{rec.plan_code}] {rec.name} - {rec.price}"
            else:
                rec.display_name = rec.name or ''


    #####################
    # Constraints       #
    #####################

    @api.constrains('price')
    def _check_price(self):
        for rec in self:
            if rec.price:
                if rec.price < 0:
                    raise ValidationError(
                        "You cannot sell a plan for negative price."
                    )

    @api.constrains('duration_days')
    def _check_duration_days(self):
        for rec in self:
            if rec.duration_days <= 0:
                raise ValidationError(
                    "Duration must be at least 1 day."
                )












