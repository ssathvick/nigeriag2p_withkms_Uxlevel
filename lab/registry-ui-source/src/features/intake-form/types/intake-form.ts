import { UploadedDocument } from '@/shared/types';


export type IntakeFormStatus = 'DRAFT' | 'SUBMITTED' | 'FINALIZED';
export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

export interface IntakeForm {
    form_description: string;
    form_id: string;
    form_mnemonic: string;
    number_of_verifications: number;
    register_id: string;
    register_mnemonic: string;
}

export interface RenderedIntakeForm {
    form_id: string;
    register_id: string;
    form_mnemonic: string;
    form_description: string;
    number_of_verifications: number;
    used_only_in_ingestion_pipeline: boolean;
    tabs: IntakeFormTab[];
}

export interface IntakeFormTab {
    tab_id: string;
    tab_label: string;
    tab_order: number;
    form_id: string;
    sections: IntakeFormSection[];
}
export interface IntakeFormSection {
    section_register_id: string;
    register_id: string;
    section_id: string;
    tab_section_id: string;
    section_mnemonic: string;
    section_description: string | null;
    register_relation: string;
    register_purpose: string;
    is_list: boolean;
    is_core_section: boolean;
    is_primary_section: boolean;
    documents_required: boolean;
    cr_auto_approve_for_agent_portal: boolean;
    cr_auto_approve_for_bene_portal: boolean;
    cr_auto_approve_for_partner: boolean;
    cr_auto_approve_for_staff_portal: boolean;
    no_of_verifications_required: number;
    section_weightage: number;
    section_order: number;
    section_ui_schema: any;
}
export interface DisplayField {
    field_name: string;
    value: any | null;
    order: number;
}
export interface IntakeFormSubmission {
    review_history?: any[];
    application_reference?: string;
    remarks?: string|null;
    record_name: string | null;
    submission_id: string;
    form_id: string;
    register_id: string;
    partner_id: string | null;
    submission_source: string;

    draft_status: 'DRAFT' | 'FINAL';
    approval_status: ApprovalStatus | string;

    number_of_verifications_required: number;
    number_of_verifications_done: number;
    awe_request_id?: string | null;
    awe_request_status_summary?: string | null;

    created_by: string;
    first_created_at: string;
    last_updated_at: string;
    finalized_at: string | null;

    approved_by: string | null;
    approved_at: string | null;

    register_ingest_process_attempts: number;
    register_ingest_process_status: string;
    register_ingest_process_last_error_code: string | null;
    register_ingest_processed_timestamp: string | null;

    deduplication_intake_forms_attempts: number | null;
    deduplication_intake_forms_error: string | null;
    deduplication_intake_forms_process_timestamp: string | null;

    deduplication_register_forms_attempts: number | null;
    deduplication_register_error: string | null;
    deduplication_register_process_timestamp: string | null;

    deduplication_status_vs_intake_forms: string | null;
    deduplication_status_vs_register: string | null;

    display_fields: DisplayField[];
    section_payloads: any | null;
}




export interface SectionPayload {
    section_id: string;
    section_register_id: string;
    is_list: boolean;
    records: any[];
    documents?: UploadedDocument[];
}

export interface SectionChanges {
    section_id?: string;
    section_register_id?: string;
    records: unknown[];
    files?: unknown[];
}

export interface Verification {
    verification_id: string;
    verified_by: string;
    verified_at: string;
    verification_observations: string;
    is_approved: boolean;
}

export interface VerificationStats {
    totalRequired: number;
    totalDone: number;
}
