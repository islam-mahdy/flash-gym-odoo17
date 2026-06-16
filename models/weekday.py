from odoo import fields, models


class GymWeekday(models.Model):
    _name = 'gym.weekday'
    _description = 'Weekday'
    _order = 'day_number'

    name = fields.Char(string='Day', required=True)
    day_number = fields.Integer(string='Day Number')