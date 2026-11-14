import { NestedValues } from '@/shared/types/types';

export const APPROVAL_CHANGE_REQUEST_ACTIONS = {
    view: 'approvalChangeRequest:view',
    create: 'approvalChangeRequest:create',
} as const;

export type ApprovalChangeRequestAction = NestedValues<typeof APPROVAL_CHANGE_REQUEST_ACTIONS>;
