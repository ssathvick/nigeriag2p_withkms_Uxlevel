import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_DATA_MODELS_ACTIONS } from "@/features/configuration/shared/utils/configurationDataModels.actions";

export default function RegistersConfigLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_DATA_MODELS_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
