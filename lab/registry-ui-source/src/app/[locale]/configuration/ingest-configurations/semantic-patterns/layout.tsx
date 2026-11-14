import RequireAction from "@/components/shared/RequireAction";
import { CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS } from "@/features/configuration/shared/utils/configurationSemanticPatterns.actions";

export default function SemanticPatternsLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
