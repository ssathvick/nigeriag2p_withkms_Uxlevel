from odoo import models, api, _
from odoo.exceptions import AccessError

class G2PProgramDefinition(models.Model):
    _inherit = "g2p.program.definition"

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('g2p_pbms.group_program_super_administration'):
            raise AccessError(_("Only users in the Program Super Administration group can create programs."))

        record = super().create(vals)

        # Create the program-specific group under g2p_pbms_program_access
        group_name = record.program_mnemonic
        if not self.env['res.groups'].search([('name', '=', group_name)], limit=1):
            self.env['res.groups'].create({
                'name': group_name,
                'category_id': self.env.ref('g2p_pbms_program_access.g2p_pbms_program_access').id,
            })
        return record

    def write(self, vals):
        for record in self:
            if 'program_mnemonic' in vals:
                # Only super admins can change program_mnemonic
                if not self.env.user.has_group('g2p_pbms.group_program_super_administration'):
                    raise AccessError(_("Only users in the Program Super Administration group can change the program mnemonic."))

                old_mnemonic = record.program_mnemonic
                new_mnemonic = vals['program_mnemonic']

                # Delete old group
                old_group = self.env['res.groups'].search([('name', '=', old_mnemonic)], limit=1)
                if old_group:
                    old_group.unlink()

                # Create new group with new mnemonic
                self.env['res.groups'].create({
                    'name': new_mnemonic,
                    'category_id': self.env.ref('g2p_pbms_program_access.g2p_pbms_program_access').id,
                })

        return super().write(vals)

    def unlink(self):
        if not self.env.user.has_group('g2p_pbms.group_program_super_administration'):
            raise AccessError(_("Only users in the Program Super Administration group can delete programs."))

        for record in self:
            group = self.env['res.groups'].search([('name', '=', record.program_mnemonic)], limit=1)
            if group:
                group.unlink()
        return super().unlink()
