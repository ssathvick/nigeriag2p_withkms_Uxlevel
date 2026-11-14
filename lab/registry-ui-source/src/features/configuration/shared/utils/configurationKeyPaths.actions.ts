import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_KEY_PATHS_ACTIONS = {
    view: "ingestKeyPath:view",
    create: "ingestKeyPath:create",
    edit: "ingestKeyPath:edit",
    delete: "ingestKeyPath:delete",
} as const;

export type ConfigurationKeyPathsAction = NestedValues<typeof CONFIGURATION_KEY_PATHS_ACTIONS>;
