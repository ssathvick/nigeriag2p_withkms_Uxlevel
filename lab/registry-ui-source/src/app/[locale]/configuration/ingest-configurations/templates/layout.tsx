import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_INGESTION_TEMPLATES_ACTIONS } from "@/features/configuration/shared/utils/configurationIngestionTemplates.actions";

export default function IngestTemplatesLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_INGESTION_TEMPLATES_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
