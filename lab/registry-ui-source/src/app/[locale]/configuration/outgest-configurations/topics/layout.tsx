import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_OUTGESTION_TOPICS_ACTIONS } from "@/features/configuration/shared/utils/configurationOutgestionTopics.actions";

export default function OutgestTopicsLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_OUTGESTION_TOPICS_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
