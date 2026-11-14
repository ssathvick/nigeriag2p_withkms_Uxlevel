import RequireAction from '@/components/shared/RequireAction';
import { VERIFICATION_CHANGE_REQUEST_ACTIONS } from '@/features/change-request/utils/verificationChangeRequest.actions';
import { VERIFICATION_INTAKE_FORM_ACTIONS } from '@/features/intake-form/utils/verificationIntakeForm.actions';

export default function TasksLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction
            anyOf={[
                VERIFICATION_CHANGE_REQUEST_ACTIONS.create,
                VERIFICATION_INTAKE_FORM_ACTIONS.create,
            ]}
        >
            {children}
        </RequireAction>
    );
}
