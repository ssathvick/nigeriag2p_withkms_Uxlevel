from odoo import models, fields, api

class G2PAgencyProgramBenefitCodes(models.Model):
    _name = 'g2p.agency.program.benefit.codes'
    _description = 'Agency Program Benefit Codes'

    agency_id = fields.Many2one(
        'g2p.agency',
        string='Agency',
        required=True,
        help='The agency this benefit code is associated with.'
    )
    program_id = fields.Many2one(
        'g2p.program.definition',
        string='Program',
        required=True,
        help='The program this benefit code is associated with.'
    )
    benefit_code_id = fields.Many2one(
        'g2p.benefit.codes',
        string='Benefit Code',
        required=True,
        help='Select the benefit code for this agency and program.'
    )

    benefit_codes = fields.Many2many(
        "g2p.benefit.codes",
        compute="_compute_benefit_codes",
        string="Benefit Codes",
        store=True,
    )
    # TODO: rename to custom_data
    additional_info = fields.Text(
        string='Custom Data',
        help='Additional info related to this agency program benefit code',
        required=False
    )

    # Related fields from agency_id
    agency_mnemonic = fields.Char(
        related='agency_id.agency_mnemonic',
        string='Agency Mnemonic',
        store=True,
        readonly=True
    )
    agency_name = fields.Char(
        related='agency_id.name',
        string='Agency Name',
        store=True,
        readonly=True
    )

    # Related fields from program_id
    program_mnemonic = fields.Char(
        related='program_id.program_mnemonic',
        string='Program Mnemonic',
        store=True,
        readonly=True
    )
    program_description = fields.Char(
        related='program_id.description',
        string='Program Description',
        store=True,
        readonly=True
    )
    target_registry = fields.Selection(
        related='program_id.target_registry',
        string='Target Registry',
        store=True,
        readonly=True
    )
    program_status = fields.Selection(
        related='program_id.program_status',
        string='Program Status',
        store=True,
        readonly=True
    )

    # Related fields from benefit_code_id
    benefit_mnemonic = fields.Char(
        related='benefit_code_id.benefit_mnemonic',
        string="Benefit Mnemonic",
        store=True,
        readonly=True
    )
    benefit_type = fields.Selection(
        related='benefit_code_id.benefit_type',
        string="Benefit Type",
        store=True,
        readonly=True
    )
    measurement_unit = fields.Char(
        related='benefit_code_id.measurement_unit',
        string="Measurement Unit",
        store=True,
        readonly=True
    )
    benefit_description = fields.Text(
        related='benefit_code_id.benefit_description',
        string="Benefit Description",
        store=True,
        readonly=True
    )

    _sql_constraints = [
        (
            "unique_agency_program_benefit_code",
            "unique(agency_id, program_id, benefit_code_id)",
            "Each benefit code can only be assigned once per agency and program."
        )
    ]

    @api.depends('program_id')
    def _compute_benefit_codes(self):
        for rec in self:
            program_benefit_codes = self.env['g2p.program.benefit.codes'].search([
                ('program_id', '=', rec.program_id.id)
            ])
            filtered_benefit_codes = program_benefit_codes.filtered(
                lambda pb: pb.benefit_type != 'CASH_DIGITAL'
            ).mapped('benefit_code_id')
            rec.benefit_codes = filtered_benefit_codes
