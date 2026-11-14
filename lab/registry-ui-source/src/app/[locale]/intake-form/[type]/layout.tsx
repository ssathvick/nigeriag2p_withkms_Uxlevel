import RequireAction from "@/components/shared/RequireAction";
import { INTAKE_FORM_ACTIONS } from "@/features/intake-form/utils/intakeForm.actions";

export default function IntakeFormLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={INTAKE_FORM_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
