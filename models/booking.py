from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymBooking(models.Model):
    _name = 'gym.booking'
    _description = 'Flash Gym Booking'
    _rec_name = 'member_id'
    _order = 'booking_date desc'

    member_id = fields.Many2one(
        'gym.member', 'Member', required=True
    )
    class_id = fields.Many2one(
        'gym.class', 'Class', required=True
    )
    booking_date = fields.Date(
        default=lambda self: fields.Date.today()
    )

    state = fields.Selection([
        ('confirmed', 'Confirmed'),
        ('waitlisted', 'Waitlisted'),
        ('cancelled', 'Cancelled'),
    ], default='confirmed')

    attended = fields.Boolean(
        string='Attended',
    )
    cancellation_reason = fields.Char()


    #####################
    # Constraints       #
    #####################

    @api.constrains('class_id.state', 'state')
    def _check_capacity_and_class_state(self):
        for rec in self:
            if rec.state != 'confirmed':
                continue
            if rec.class_id.state == 'cancelled':
                raise ValidationError(
                    "You cannot enroll in this class because it is cancelled."
                )
            enrolled_trainers = self.search([
                ('class_id', '=', rec.class_id.id),
                ('state', '=', 'confirmed'),
                ('id', '!=', rec.id)
            ])
            if len(enrolled_trainers) >= rec.class_id.capacity:
                raise ValidationError(
                    f"'{rec.class_id.name}' is fully booked "
                    f"({rec.class_id.capacity} spots)."
                )
            if rec.class_id.requires_membership_class:
                active_membership = self.env['gym.membership'].search([
                    ('member_id', '=', rec.member_id.id),
                    ('state', '=', 'active'),
                ], limit=1)
                if not active_membership or \
                        not active_membership.plan_id.includes_classes:
                    raise ValidationError(
                        "Your current plan does not include "
                        "group class access."
                    )

    @api.constrains('class_id', 'member_id')
    def _check_no_duplicate_booking(self):
        for rec in self:
            if rec.class_id and rec.member_id:

                duplicate = self.search([
                    ('member_id', '=', rec.member_id.id),
                    ('class_id', '=', rec.class_id.id),
                    ('state', '=', 'confirmed'),
                    ('id', '!=', rec.id),
                ], limit=1)
                if duplicate:
                    raise ValidationError(
                        f"'{rec.member_id.name}' already has a confirmed "
                        f"booking for this class."
                    )


    #####################
    # Work Flows        #
    #####################

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
            rec.class_id._compute_enrolled()




    #####################
    # Onchange Warning  #
    #####################
    @api.onchange('class_id')
    def _onchange_class_id(self):
        if self.class_id and self.class_id.available_spots == 0:
            self.state = 'waitlisted'
            return {
                'warning': {
                    'title': 'Class Full',
                    'message': f"'{self.class_id.name}' has no available spots. "
                               f"This booking will be waitlisted.",
                }
            }

    #####################
    # Computed Methods  #
    #####################












