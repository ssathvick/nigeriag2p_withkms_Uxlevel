import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_TABS_ACTIONS = {
    view: "registerTab:view",
    create: "registerTab:create",
    edit: "registerTab:edit",
    delete: "registerTab:delete",
} as const;

export type ConfigurationTabsAction = NestedValues<typeof CONFIGURATION_TABS_ACTIONS>;
