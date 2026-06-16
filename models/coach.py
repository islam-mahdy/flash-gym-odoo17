from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymCoach(models.Model):
    _name = 'gym.coach'
    _description = 'Flash Gym Coach'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = 'name'

    name = fields.Char(
        required=True, tracking=True, string='Full Name',
    )

    coach_code = fields.Char(
        default=lambda self: self.env['ir.sequence'].next_by_code('gym.coach.seq'),
        readonly=True, copy=False,
    )
    employee_type = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('freelance', 'Freelance'),
    ], required=True, tracking=True)

    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email Address')
    hire_date = fields.Date(string='Hire Date')
    years_experience = fields.Integer(string='Years Experience')

    specialization_ids = fields.Many2many(
        'gym.specialization',
        string='Specializations',
    )
    certification_ids = fields.One2many(
        'gym.coach.certification',
        'coach_id',
        string='Certifications'
    )

    active = fields.Boolean(default=True)

    bio = fields.Text(string='Biography')



    #####################
    # SQL Constraints   #
    #####################

    _sql_constraints = [
        (
            'unique_coach_code',
            'UNIQUE (coach_code)',
            "This code is used by another Coach"
        ),

        (
            'unique_phone',
            'UNIQUE (phone)',
            "Please enter your correct phone number."
            "This phone is used by another Coach"
        ),

        (
            'unique_email',
            'UNIQUE (email)',
            "Please enter your correct email address."
            "This email address is used by another Coach"
        ),
    ]




    #####################
    # Computed Methods  #
    #####################

    def _compute_display_name(self):
        for rec in self:
            if rec.coach_code:
                specs = rec.specialization_ids.mapped('name')
                rec.display_name = f"[{rec.coach_code}] {rec.name} - {', '.join(specs[:2])}"
            else:
                rec.display_name = rec.name or ''


    #####################
    # Constraints       #
    #####################

    @api.constrains('years_experience')
    def _check_years_experience(self):
        for rec in self:
            if rec.years_experience < 0:
                raise ValidationError(
                    "The coach experience years cannot be negative."
                )

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError(
                    f"'{rec.email}' is not a valid email address."
                )










