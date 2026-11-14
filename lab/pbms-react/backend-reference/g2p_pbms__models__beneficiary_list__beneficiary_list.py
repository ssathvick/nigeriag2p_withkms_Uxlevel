import uuid
from odoo import models, fields, api


class G2PBeneficiaryList(models.Model):
    _name = "g2p.beneficiary.list"
    _description = "G2P Beneficiary List"
    _rec_name = "mnemonic"

    beneficiary_list_id = fields.Char(string='Beneficiary List ID', readonly=True, required=True, default=lambda self: str(uuid.uuid4()))
    mnemonic = fields.Char(string="Mnemonic", required=True)
    program_id = fields.Many2one("g2p.program.definition", string="G2P Program", compute="_compute_program_id", store=True, readonly=True)
    enrollment_cycle_id = fields.Many2one("g2p.enrollment.cycle", string="Enrollment Cycle", required=False)
    disbursement_cycle_id = fields.Many2one("g2p.disbursement.cycle", string="Disbursement Cycle", required=False)

    brief = fields.Text(string="Brief")
    eligibility_process_status = fields.Selection(
        [
            ("not_applicable", "not applicable"),
            ("pending", "pending"),
            ("processing", "processing"),
            ("complete", "complete"),
        ],
        string="Eligibility Process Status",
        default="pending",
    )
    eligibility_number_of_attempts = fields.Integer(string="Eligibility Number of Attempts", default=0)
    eligibility_latest_error_code = fields.Char(string="Eligibility Latest Error Code", default=None)
    eligibility_processed_date = fields.Datetime(string="Eligibility Processed Date", default=None)

    entitlement_process_status = fields.Selection(
        [
            ("not_applicable", "not applicable"),
            ("pending", "pending"),
            ("processing", "processing"),
            ("complete", "complete"),
        ],
        string="Entitlement Process Status",
        default="not_applicable",
    )
    entitlement_number_of_attempts = fields.Integer(string="Entitlement Number of Attempts", default=0)
    entitlement_latest_error_code = fields.Char(string="Entitlement Latest Error Code", default=None)
    entitlement_processed_date = fields.Datetime(string="Entitlement Processed Date", default=None)

    envelope_creation_status = fields.Selection(
        [
            ("not_applicable", "not applicable"),
            ("pending", "pending"),
            ("processing", "processing"),
            ("complete", "complete"),
        ],
        string="Disbursement Envelope Status",
        default="not_applicable",
    )
    envelope_creation_number_of_attempts = fields.Integer(string="Envelope Creation Number of Attempts", default=0)
    envelope_creation_latest_error_code = fields.Char(string="Envelope Creation Latest Error Code", default=None)
    envelope_creation_processed_date = fields.Datetime(string="Envelope Creation Processed Date", default=None)

    disbursement_batch_creation_status = fields.Selection(
        [
            ("not_applicable", "not applicable"),
            ("pending", "pending"),
            ("processing", "processing"),
            ("complete", "complete"),
        ],
        string="Disbursement Envelope Status",
        default="not_applicable",
    )
    dbc_number_of_attempts = fields.Integer(string="Disbursement Batch Creation Number of Attempts", default=0)
    dbc_latest_error_code = fields.Char(string="Disbursement Batch Creation Latest Error Code", default=None)
    dbc_processed_date = fields.Datetime(string="Disbursement Batch Creation Processed Date", default=None)

    number_of_registrants = fields.Integer(string="Number of Registrants", default=0)
    number_of_entitlements_processed = fields.Integer(string="Number of Entitlements Processed", default=0)

    list_stage = fields.Selection(
        [
            ("enrollment", "ENROLLMENT"),
            ("disbursement", "DISBURSEMENT")
        ],
        string="List Stage",
    )
    approval_date = fields.Date(string="Approval Date", default=None, readonly=True)
    list_workflow_status = fields.Selection(
        [
            ("initiated", ""),
            ("approved_final_enrolment", "APPROVED FINAL ENROLMENT"),
            ("approved_for_disbursement", "APPROVED FOR DISBURSEMENT"),
        ],
        string="List Workflow Status",
        default="initiated",
    )
    verification_ids = fields.One2many(
        "storage.file",
        "beneficiary_list_id",
        string="Community Verification",
    )
    creation_date = fields.Datetime(string="Creation Date", default=fields.Datetime.now , readonly=True)
    processed_date = fields.Datetime(string="Processed Date", default=None, readonly=True)


    @api.depends('enrollment_cycle_id.program_id', 'disbursement_cycle_id.program_id')
    def _compute_program_id(self):
        for record in self:
            if record.enrollment_cycle_id:
                record.program_id = record.enrollment_cycle_id.program_id
                record.list_stage = "enrollment"
            elif record.disbursement_cycle_id:
                record.program_id = record.disbursement_cycle_id.program_id
                record.list_stage = "disbursement"

    def action_open_summary_wizard(self):
        if (
            self.list_stage == 'enrollment'
            and self.list_workflow_status != 'approved_final_enrollment'
            and getattr(self.program_id, 'auto_approve_enrolment', False)
            and getattr(self.program_id, 'verifications_for_enrolment', 0) == 0
        ):
            self.list_workflow_status = 'approved_final_enrolment'
            self.approval_date = fields.Date.context_today(self)
            if self.enrollment_cycle_id:
                self.env['g2p.enrollment.cycle'].browse(self.enrollment_cycle_id.id).write({
                    'approved_for_enrollment': True,
                })

        if (
            self.list_stage == 'disbursement'
            and self.list_workflow_status != 'approved_for_disbursement'
            and getattr(self.program_id, 'auto_approve_disbursement', False)
            and getattr(self.program_id, 'verifications_for_disbursement', 0) == 0
        ):
            self.list_workflow_status = 'approved_for_disbursement'
            self.approval_date = fields.Date.context_today(self)
            if self.disbursement_cycle_id:
                self.env['g2p.disbursement.cycle'].browse(self.disbursement_cycle_id.id).write({
                    'approved_for_disbursement': True,
                })

        self.ensure_one()
        wizard_vals = {
            "target_registry": self.program_id.target_registry,
            "mnemonic": self.mnemonic,
            "brief": self.brief,
            "program_id": self.program_id.id,
            "beneficiary_list_id": self.id,
            "beneficiary_list_uuid": self.beneficiary_list_id,
            "enrollment_cycle_id": self.enrollment_cycle_id,
            "disbursement_cycle_id": self.disbursement_cycle_id,
            "list_stage": self.list_stage,
            "list_workflow_status": self.list_workflow_status,
            "enrollment_start_date": self.enrollment_cycle_id.enrollment_start_date if self.enrollment_cycle_id else None,
            "enrollment_end_date": self.enrollment_cycle_id.enrollment_end_date if self.enrollment_cycle_id else None,
            "disbursement_cycle_mnemonic": self.disbursement_cycle_id.cycle_mnemonic if self.disbursement_cycle_id else None,
            "approved_for_disbursement": self.disbursement_cycle_id.approved_for_disbursement if self.disbursement_cycle_id else None,
        }

        wizard = self.env["g2p.bgtask.summary.wizard"].create(wizard_vals)
        return {
            "name": "Eligibility Summary Details",
            "view_mode": "form",
            "res_model": "g2p.bgtask.summary.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "current",
            'context': {
                'default_target_registry': self.program_id.target_registry,
                'default_program_id': self.program_id.id,
                'default_beneficiary_list_id': self.beneficiary_list_id,
            },
        }
