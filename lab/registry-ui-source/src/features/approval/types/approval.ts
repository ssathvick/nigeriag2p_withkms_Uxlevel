export interface ApprovalTask {
    id: string;
    request_id: string;
    stage_id: string;
    stage_order: number;
    assignee: string;
    kind?: 'approver' | 'observer';
    status: string;
    claimed_at?: string | null;
    completed_at?: string | null;
    due_at?: string | null;
    created_at: string;
    artifact_type?: string | null;
    artifact_id?: string | null;
    policy_key?: string | null;
    context?: Record<string, unknown> | null;
    search_text?: string | null;
    decision_action?: string | null;
    decision_comment?: string | null;
}
