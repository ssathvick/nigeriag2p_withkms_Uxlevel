import { NestedValues } from '@/shared/types/types';

export const APPROVAL_TASK_ACTIONS = {
    view: 'approvalTask:view',
} as const;

export type ApprovalTaskAction = NestedValues<typeof APPROVAL_TASK_ACTIONS>;
