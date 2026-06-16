from odoo import fields, models

class GYMSpecialization(models.Model):
    _name = 'gym.specialization'
    _description = 'Flash Gym Specialization'
    _order = 'name'


    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

