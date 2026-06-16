from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GymClassTemplate(models.Model):
    _name = 'gym.class.template'
    _description = 'Flash Gym Class Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']




    name = fields.Char(string='Name', required=True)

    coach_id = fields.Many2one(
        'gym.coach', 'Coach', required=True,tracking=True
    )
    specialization_id = fields.Many2one(
        'gym.specialization', 'Class type', tracking=True
    )

    scheduled_date = fields.Date(required=True)

    start_time = fields.Datetime(required=True)
    duration_hours = fields.Float(default=1)

    capacity = fields.Integer(
        help="Maximum number of members", default=20
    )

    requires_membership_class = fields.Boolean(
        string='Requires Class Access in Plan',
        default=True,
    )

    recurrence_days = fields.Many2many(
        'gym.weekday', string='Recurrence Days',
    )
    generation_start = fields.Datetime()
    generation_end = fields.Datetime()

    generated_class_ids = fields.One2many(
        'gym.class', 'template_id', string='Generated Classes'
    )

    generated_count = fields.Integer(compute='_compute_generation_count')


    #####################
    # Computed Methods  #
    #####################

    @api.depends('generated_class_ids')
    def _compute_generation_count(self):
        for rec in self:
            rec.generated_count = len(rec.generated_class_ids)


    #####################
    # Constraints       #
    #####################

    @api.constrains('generation_start', 'generation_end')
    def _check_generation_start(self):
        for rec in self:
            if rec.generation_start and rec.generation_end:
                if rec.generation_start > rec.generation_end:
                    raise ValidationError(
                        "Generation start cannot be after than generation end"
                    )
                delta = (rec.generation_end - rec.generation_start).days
                if delta > 365:
                    raise ValidationError(
                        "Generation range cannot exceed 365 days."
                    )


    #####################
    # CRUD Operations   #
    #####################


    #####################
    # Work Flows        #
    #####################







