export interface Register {
    register_id: string;
    register_mnemonic: string;
    register_subject: string;
    register_description: string;
    master_register_id: string | null;
    master_register_mnemonic: string;
    register_purpose?: string;
    register_rank?: number;
    register_icon?: string;
    dedup_is_enabled?: boolean;
    dedup_threshold_score?: number;
    has_data?: boolean;
    has_image?: boolean;
    program_id?: string;
    functional_id_generation_required?: boolean;
    completion_score_required?: boolean;
}

export interface ScoreDefinition {
    score_definition_id: string;
    register_mnemonic?: string;
    score_type: string;
    is_enabled: boolean;
}

export interface ScoreContributingAttribute {
    contributing_attribute_id: string;
    attribute_name: string;
    attribute_computation_required: boolean;
    attribute_computation_value: Record<string, unknown>;
    attribute_weight: number;
    attribute_weightage?: number;
}
