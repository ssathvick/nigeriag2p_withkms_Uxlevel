export interface IncomingMessage {
    ingest_id: string;

    partner_id: string;
    partner_mnemonic: string;

    data_model_id: string;
    data_model_mnemonic: string;

    ingest_message_id: string;
    ingest_correlation_id: string;

    receipt_date_time: string;

    classification_status: string;
    classification_date_time?: string;
    classification_number_of_attempts?: string;
    classification_latest_error_code?: string;

    change_request_id?: string | null;

    register_id?: string | null;
    register_mnemonic?: string;

    section_id?: string;
    section_mnemonic?: string;

    intake_form_mnemonic?: string;
    intake_form_submission_id?: string | null;

    tab_id?: string;

    semantic_pattern_id?: string;
    template_id?: string;
    template_file_id?: string;

    pipeline_action?: string | null;

    transformation_status?: string | null;
    transformation_date_time?: string | null;
    transformation_number_of_attempts?: number;
    transformation_latest_error_code?: string | null;

    ingestion_status?: string | null;
    ingestion_date_time?: string | null;
    ingestion_number_of_attempts?: number;
    ingestion_latest_error_code?: string | null;
}
