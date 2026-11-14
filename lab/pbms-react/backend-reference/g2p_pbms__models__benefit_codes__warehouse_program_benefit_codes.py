from odoo import models, fields, api


class G2PWarehouseProgramBenefitCodes(models.Model):
    _name = 'g2p.warehouse.program.benefit.codes'
    _description = 'Warehouse Program Benefit Codes'

    warehouse_id = fields.Many2one(
        'g2p.warehouse',
        string='Warehouse',
        required=True,
        help='The warehouse this benefit code is associated with.'
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
        help='Select the benefit code for this warehouse and program.'
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
        help='Additional info related to this warehouse program benefit code',
        required=False
    )

    # Related fields from warehouse_id (see warehouse.py)
    warehouse_mnemonic = fields.Char(
        related='warehouse_id.warehouse_mnemonic',
        string='Warehouse Mnemonic',
        store=True,
        readonly=True
    )
    warehouse_name = fields.Char(
        related='warehouse_id.name',
        string='Warehouse Name',
        store=True,
        readonly=True
    )
    warehouse_is_sponsor_bank = fields.Boolean(
        related='warehouse_id.is_sponsor_bank',
        string='Is Sponsor Bank',
        store=True,
        readonly=True
    )

    # Related fields from program_id (see program_definition.py)
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

    # Related fields from benefit_code_id (see benefit_codes.py)
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
            "unique_warehouse_program_benefit_code",
            "unique(warehouse_id, program_id, benefit_code_id)",
            "Each benefit code can only be assigned once per warehouse and program."
        )
    ]


    @api.depends('program_id')
    def _compute_benefit_codes(self):
        for rec in self:
            program_benefit_codes = self.env['g2p.program.benefit.codes'].search([
                ('program_id', '=', rec.program_id.id)
            ])
            filtered_benefit_codes = program_benefit_codes.mapped('benefit_code_id')

            if rec.warehouse_is_sponsor_bank:
                # Filter out benefit codes with benefit_type == 'CASH_DIGITAL'
                filtered_benefit_codes = program_benefit_codes.filtered(
                    lambda pb: pb.benefit_type in ('CASH_DIGITAL', 'CASH_PHYSICAL')
                ).mapped('benefit_code_id')
            else:
                filtered_benefit_codes = program_benefit_codes.filtered(
                    lambda pb: pb.benefit_type not in ('CASH_DIGITAL', 'CASH_PHYSICAL')
                ).mapped('benefit_code_id')

            rec.benefit_codes = filtered_benefit_codes
