from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GymCoachCertification(models.Model):
    _name = 'gym.coach.certification'
    _description = 'Flash Gym Coach Certification'
    _rec_name = 'coach_id'
    _order = 'issued_date desc'


    coach_id = fields.Many2one(
        'gym.coach', 'Coach',
        required=True, ondelete='cascade',
    )
    certification_name = fields.Char(
        string='Certification Name', required=True
    )
    issued_by = fields.Char()
    issued_date = fields.Date(string='Issued Date')
    expiry_date = fields.Date(string='Expiry Date')



    #####################
    # Constraints       #
    #####################

    @api.constrains('issued_date', 'expiry_date')
    def _check_date(self):
        for rec in self:
            if rec.issued_date and rec.expiry_date:
                if rec.expiry_date <= rec.issued_date:
                    raise ValidationError(
                        "Expiry date must be after issuing date"
                    )












