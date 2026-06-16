from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymClass(models.Model):
    _name = 'gym.class'
    _description = 'Flash Gym Class'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start__date desc'



    name = fields.Char(string='Name', required=True)
    class_code = fields.Char(
        default=lambda self:self.env['ir.sequence'].next_by_code('gym.class.seq'),
        readonly=True, copy=False
    )
    coach_id = fields.Many2one(
        'gym.coach', 'Coach', required=True,tracking=True
    )
    specialization_id = fields.Many2one(
        'gym.specialization', 'Class type', tracking=True
    )

    scheduled_date = fields.Date(required=True)

    start__date = fields.Float(
        default=9.0,
        string='Start Date', required=True,
        )
    duration_hours = fields.Float(default=1)
    end__date = fields.Float(
        string='End Date',
        compute='_compute_start__end__date',
        store=True,
    )
    capacity = fields.Integer(
        help="Maximum number of members"
    )

    available_spots = fields.Integer(
        string='Available Spots',
        compute='_compute_enrolled',
        store=True,
    )
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled', tracking=True)
    booking_ids = fields.One2many('gym.booking', 'class_id', string='Bookings')
    requires_membership_class = fields.Boolean(
        string='Requires Class Access in Plan',
        default=True,
    )

    enrolled_count = fields.Integer(
        string='Enrolled Count',
        compute='_compute_enrolled',
        store=True,
    )

    notes = fields.Text(string='Notes')


    #####################
    # CRUD Operations   #
    #####################

    @api.model
    def create(self, vals):
        res = super(GymClass, self).create(vals)
        if res.scheduled_date < fields.Date.today():
            raise ValidationError(
                "Scheduled Class cannot be in the past."
            )
        return res


    #####################
    # Work Flows        #
    #####################



    #####################
    # Computed Methods  #
    #####################

    @api.depends('booking_ids', 'booking_ids.state')
    def _compute_enrolled(self):
        for rec in self:
            active_bookings = rec.booking_ids.filtered(
                lambda b: b.state == 'confirmed'
            )
            rec.enrolled_count = len(active_bookings)
            rec.available_spots = rec.capacity - rec.enrolled_count

    @api.depends('start__date', 'duration_hours')
    def _compute_start__end__date(self):
        for rec in self:
            if rec.start__date:
                rec.end__date = rec.start__date + rec.duration_hours




    #####################
    # Constraints       #
    #####################

    @api.constrains('duration_hours')
    def _check_duration_hours(self):
        for rec in self:
            if rec.duration_hours <= 0:
                raise ValidationError(
                    "Duration Hours must be greater than 0"
                )

    @api.constrains('capacity')
    def _check_capacity(self):
        for rec in self:
            if rec.capacity <= 0:
                raise ValidationError(
                    "capacity must be greater than 0"
                )


    @api.constrains('coach_id', 'specialization_id')
    def _check_coach_id(self):
        for rec in self:
            if rec.specialization_id and rec.coach_id:
                if rec.specialization_id not in rec.coach_id.specialization_ids:
                    raise ValidationError(
                        f"Coach '{rec.coach_id.name}' is not qualified "
                        f"for '{rec.specialization_id.name}' classes."
                )










