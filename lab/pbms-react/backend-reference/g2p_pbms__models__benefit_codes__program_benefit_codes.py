from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PProgramBenefitCodes(models.Model):
    _name = "g2p.program.benefit.codes"
    _description = "Program Benefit Codes"
    _table = "g2p_program_benefit_codes"

    program_id = fields.Many2one(
        'g2p.program.definition',
        string="Program",
        required=True,
        ondelete='cascade',
        help="The program this benefit code is associated with."
    )
    benefit_code_id = fields.Many2one(
        'g2p.benefit.codes',
        string="Benefit Code",
        required=True,
        help="Select the benefit code for this program."
    )

    max_quantity = fields.Float(
        string="Maximum Quantity",
        required=True,
        digits=(16,4),
        help="Maximum quantity allowed for this benefit code in the program."
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
            "unique_program_benefit_code",
            "unique(program_id, benefit_code_id)",
            "Each benefit code can only be assigned once per program."
        )
    ]

    def _round_and_trim_float(self, value, decimal_places):
        """
        Rounds the value to the given decimal_places using Odoo's Float.round().
        Removes insignificant trailing zeros and any trailing decimal,
        and returns a float or int as appropriate.
        """
        if not isinstance(value, float):
            return value
        rounded = fields.Float.round(value, precision_digits=decimal_places)
        return rounded

    @api.model
    def create(self, vals):
        benefit_code = None
        decimal_places = 5  # Fallback
        if 'benefit_code_id' in vals:
            benefit_code = self.env['g2p.benefit.codes'].browse(vals['benefit_code_id'])
            decimal_places = benefit_code.decimal_places or 0
        if 'max_quantity' in vals and isinstance(vals['max_quantity'], float):
            vals['max_quantity'] = self._round_and_trim_float(vals['max_quantity'], decimal_places)
        return super().create(vals)

    def write(self, vals):
        decimal_places = 5  # fallback
        benefit_code = self.benefit_code_id

        if benefit_code and hasattr(benefit_code, 'decimal_places'):
            decimal_places = benefit_code.decimal_places or 0
        if 'max_quantity' in vals and isinstance(vals['max_quantity'], float):
            vals['max_quantity'] = self._round_and_trim_float(vals['max_quantity'], decimal_places)
        return super().write(vals)
