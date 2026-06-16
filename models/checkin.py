from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GymCheckin(models.Model):
    _name = 'gym.checkin'
    _description = 'Gym Check-in'
    _order = 'checkin_time desc'

    member_id = fields.Many2one(
        'gym.member',
        string='Member',
        required=True,
    )
    checkin_time = fields.Datetime(
        string='Check-in Time',
        default=fields.Datetime.now,
        required=True,
    )
    checkout_time = fields.Datetime(string='Check-out Time')
    duration_minutes = fields.Float(
        string='Duration (minutes)',
        compute='_compute_duration',
        store=True,
    )
    entry_method = fields.Selection([
        ('reception', 'Reception'),
        ('self_service', 'Self-Service Kiosk'),
        ('app', 'Mobile App'),
    ], string='Entry Method', default='reception')
    notes = fields.Char(string='Notes')
    membership_id = fields.Many2one(
        'gym.membership',
        string='Membership',
        compute='_compute_membership_id',
        store=True,
    )


    ########################
    # Constraints          #
    ########################

    @api.constrains('checkin_time', 'checkout_time')
    def _check_checkout_after_checkin(self):
        for rec in self:
            if rec.checkin_time and rec.checkout_time:
                if rec.checkout_time <= rec.checkin_time:
                    raise ValidationError(
                        "Check-out time must be after check-in time."
                    )

    @api.constrains('member_id')
    def _check_member_has_active_membership(self):
        for rec in self:
            if rec.member_id:
                active = self.env['gym.membership'].search([
                    ('member_id', '=', rec.member_id.id),
                    ('state', '=', 'active'),
                ], limit=1)
                if not active:
                    raise ValidationError(
                        f"'{rec.member_id.name}' does not have an active membership. "
                        f"Check-in is not allowed."
                    )



    @api.onchange('member_id')
    def _onchange_member_id(self):
        if self.member_id and self.member_id.membership_state != 'active':
            return {
                'warning': {
                    'title': 'Member Not Active',
                    'message': f"'{self.member_id.name}' does not have an "
                               f"active membership. Check-in will be blocked "
                               f"on save.",
                }
            }

    ########################
    # Computed Methods     #
    ########################

    def _compute_display_name(self):
        for rec in self:
            if rec.member_id and rec.checkin_time:
                rec.display_name = f"{rec.member_id.name} - {rec.checkin_time.strftime('%d/%m/%Y %H:%M')}"
            else:
                rec.display_name = "New Check-in"

    @api.depends('member_id')
    def _compute_membership_id(self):
        for rec in self:
            if rec.member_id:
                active_id = self.env['gym.membership'].search([
                    ('member_id', '=', rec.member_id.id),
                    ('state', '=', 'active'),
                ], limit=1)
                if active_id:
                    rec.membership_id = active_id
                else:
                    rec.membership_id = False


    @api.depends('checkin_time', 'checkout_time')
    def _compute_duration(self):
        for rec in self:
            if rec.checkin_time and rec.checkout_time:
                delta = rec.checkout_time - rec.checkin_time
                rec.duration_minutes = delta.total_seconds() / 60
            else:
                rec.duration_minutes = 0.0




