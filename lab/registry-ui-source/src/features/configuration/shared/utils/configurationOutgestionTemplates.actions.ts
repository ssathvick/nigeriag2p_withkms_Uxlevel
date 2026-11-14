import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_OUTGESTION_TEMPLATES_ACTIONS = {
    view: "outgestTemplate:view",
    create: "outgestTemplate:create",
    edit: "outgestTemplate:edit",
    delete: "outgestTemplate:delete",
} as const;

export type ConfigurationOutgestionTemplatesAction = NestedValues<typeof CONFIGURATION_OUTGESTION_TEMPLATES_ACTIONS>;
