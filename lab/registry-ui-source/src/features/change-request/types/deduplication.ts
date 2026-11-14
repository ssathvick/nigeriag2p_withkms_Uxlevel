export interface FieldMatch {
    incoming: string;
    candidate: string;
    similarity: number;
    match_type: string;
}

export interface DeduplicationResult {
    dedup_result_id: string;
    change_request_id: string;
    internal_record_id?: string;
    candidate_change_request_id?: string;
    match_score: number;
    field_matches: Record<string, FieldMatch>;
    created_at: string;
}
