export interface Section {
    section_id: string;
    section_mnemonic: string;
    section_description: string;
    documents_required?: boolean;
    section_order?: number;
    no_of_verifications_required?: number;
    auto_approval: boolean;
    cr_auto_approve_for_bene_portal?: boolean;
    cr_auto_approve_for_agent_portal?: boolean;
    cr_auto_approve_for_staff_portal?: boolean;
    cr_auto_approve_for_partner?: boolean;
    cr_auto_approve_for_intake_form?: boolean;
    is_list: boolean;
    is_primary_section: boolean;
    is_core_section?: boolean;
    section_weightage?: number;
    section_register_id: string;
    section_ui_schema: any;
    register_id: string;
    tab_id: string;
    register_purpose: string;
    used_for_new_intake_form?: boolean;
    tab_label?: string;
    intake_form_name?: string | null;
    intake_form_description?: string | null;
}
