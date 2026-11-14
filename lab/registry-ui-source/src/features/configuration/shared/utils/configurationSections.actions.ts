import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_SECTIONS_ACTIONS = {
    view: "registerSection:view",
    create: "registerSection:create",
    edit: "registerSection:edit",
    delete: "registerSection:delete",
} as const;

export type ConfigurationSectionsAction = NestedValues<typeof CONFIGURATION_SECTIONS_ACTIONS>;
