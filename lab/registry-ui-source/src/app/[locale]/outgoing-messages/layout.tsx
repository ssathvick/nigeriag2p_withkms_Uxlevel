import RequireAction from "@/components/shared/RequireAction";
import { OUTGOING_MESSAGE_ACTIONS } from "@/features/messages/utils/outgoingMessage.actions";

export default function OutgoingMessagesLayout({ children }: { children: React.ReactNode }) {
    return (
        <RequireAction action={OUTGOING_MESSAGE_ACTIONS.view}>
            {children}
        </RequireAction>
    );
}
