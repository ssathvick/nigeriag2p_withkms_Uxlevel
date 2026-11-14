import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_REGISTRY_ACTIONS } from "@/features/configuration/shared/utils/configurationRegistry.actions";

export default function RegistryConfigLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_REGISTRY_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
