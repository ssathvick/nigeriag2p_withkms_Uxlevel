import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_INTAKE_FORM_ACTIONS } from "@/features/configuration/shared/utils/configurationIntakeForm.actions";

export default function IntakeFormConfigLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_INTAKE_FORM_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
