# -*- coding: utf-8 -*-
# Copyright 2017 Pesol (<http://pesol.es>)
#                Angel Moya <angel.moya@pesol.es>
#                Luis Adan Jimenez Hernandez <luis.jimenez@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
from datetime import datetime, timedelta


class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    auto = fields.Boolean(
        string='Auto')

    action_server_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Server Action')


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def cancel_previous_activity_auto(self):
        activity_obj = self.env['mail.activity']
        for record in self:
            activities = activity_obj.search([
                ('res_id', '=', record.res_id),
                ('res_model_id', '=', record.res_model_id.id),
                ('id', '!=', record.id)
            ])
            activities.filtered(
                lambda a: a.activity_type_id.auto
            ).unlink()

    @api.model
    def create(self, vals):
        res = super(MailActivity, self).create(vals)
        activity_type_obj = self.env['mail.activity.type']
        activity_type_id = vals.get('activity_type_id')
        if not activity_type_id:
            return res
        activity_type = activity_type_obj.browse(activity_type_id)
        if not activity_type.auto:
            return res
        res.cancel_previous_activity_auto()
        return res

    @api.multi
    def _check_mail_activity_auto(self):
        activities = self.search([]).filtered(
            lambda a: a.activity_type_id.auto and
            a.date_deadline < fields.Datetime.now())
        activity = self.env['mail.activity']
        for record in activities:
            _context = record.activity_type_id.action_server_id._context
            _context['active_id'] = record.res_id
            _context['model_id'] = record.res_model_id.id
            _context['res_model'] = record.res_model
            _context['active_model'] = record.res_model
            action = record.activity_type_id.action_server_id.with_context(
                _context
            )
            action.run()
            next_activity = record.activity_type_id.next_type_ids and \
              record.activity_type_id.next_type_ids[0]
            res_id = record.res_id
            res_model_id = record.res_model_id.id
            record.action_done()
            if next_activity:
                days = next_activity.days
                date = fields.Datetime.from_string(fields.Datetime.now())
                next_date = date + timedelta(days=days)
                activity_data = {
                    'res_id': res_id,
                    'res_model_id': res_model_id,
                    'activity_type_id': next_activity.id,
                    'date_deadline': fields.Datetime.to_string(next_date)
                }
                activity.create(activity_data)
