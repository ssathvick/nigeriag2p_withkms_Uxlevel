import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_REGISTRY_ACTIONS } from "@/features/configuration/shared/utils/configurationRegistry.actions";

export default function RegistryThemeConfigLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_REGISTRY_ACTIONS.edit}>
            {children}
        </RequireAction>
    );
}
