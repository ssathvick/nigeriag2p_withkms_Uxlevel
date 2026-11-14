import { NestedValues } from "@/shared/types/types";

export const INCOMING_MESSAGE_ACTIONS = {
    view: "incomingMessage:view",
} as const;

export type IncomingMessageAction = NestedValues<typeof INCOMING_MESSAGE_ACTIONS>;
