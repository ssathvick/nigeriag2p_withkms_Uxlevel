import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_SUBSCRIPTION_ACTIONS } from "@/features/configuration/shared/utils/configurationSubscription.actions";

export default function ManageSubscriptionLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_SUBSCRIPTION_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
