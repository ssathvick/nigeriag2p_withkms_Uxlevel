export interface Tab {
    tab_id: string;
    register_id?: string;
    tab_label: string;
    tab_order: number;
    used_for_new_intake_form: boolean;
    no_of_verifications_required: number;
    intake_form_name: string | null;
    intake_form_description: string | null;
    intake_form_auto_approve: boolean;
    is_active: boolean;
}
