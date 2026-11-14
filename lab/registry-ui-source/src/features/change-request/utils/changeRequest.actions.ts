import { NestedValues } from "@/shared/types/types";

export const CHANGE_REQUEST_ACTIONS = {
    view: "changeRequest:view",
    approve: "changeRequest:approve",
    create: "changeRequest:create"
} as const;

export type ChangeRequestAction = NestedValues<typeof CHANGE_REQUEST_ACTIONS>;
