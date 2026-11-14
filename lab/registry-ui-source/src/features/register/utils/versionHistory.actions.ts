import { NestedValues } from "@/shared/types/types";

export const VERSION_HISTORY_ACTIONS = {
    view: "registerHistory:view",
} as const;

export type VersionHistoryAction = NestedValues<typeof VERSION_HISTORY_ACTIONS>;
