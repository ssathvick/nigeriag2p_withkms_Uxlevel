import RequireAction from "@/components/shared/RequireAction";
import { REGISTER_ACTIONS } from "@/features/register/utils/register.actions";

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={REGISTER_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
