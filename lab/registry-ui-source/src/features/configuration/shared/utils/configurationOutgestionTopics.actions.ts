import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_OUTGESTION_TOPICS_ACTIONS = {
    view: "outgestTopic:view",
    create: "outgestTopic:create",
    edit: "outgestTopic:edit",
    delete: "outgestTopic:delete",
} as const;

export type ConfigurationOutgestionTopicsAction = NestedValues<typeof CONFIGURATION_OUTGESTION_TOPICS_ACTIONS>;
