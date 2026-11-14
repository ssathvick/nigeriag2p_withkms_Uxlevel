import RequireAction from "@/components/shared/RequireAction";
import { VERSION_HISTORY_ACTIONS } from "@/features/register/utils/versionHistory.actions";

export default function VersionHistoryLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={VERSION_HISTORY_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
