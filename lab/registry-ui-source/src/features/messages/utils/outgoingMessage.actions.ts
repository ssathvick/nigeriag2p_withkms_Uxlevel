import { NestedValues } from "@/shared/types/types";

export const OUTGOING_MESSAGE_ACTIONS = {
    view: "outgoingMessage:view",
} as const;

export type OutgoingMessageAction = NestedValues<typeof OUTGOING_MESSAGE_ACTIONS>;
