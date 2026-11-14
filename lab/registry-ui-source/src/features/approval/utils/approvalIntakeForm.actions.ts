import { NestedValues } from '@/shared/types/types';

export const APPROVAL_INTAKE_FORM_ACTIONS = {
    view: 'approvalIntakeForm:view',
    create: 'approvalIntakeForm:create',
} as const;

export type ApprovalIntakeFormAction = NestedValues<typeof APPROVAL_INTAKE_FORM_ACTIONS>;
