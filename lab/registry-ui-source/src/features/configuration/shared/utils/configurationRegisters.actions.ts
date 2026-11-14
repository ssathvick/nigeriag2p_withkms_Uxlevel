import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_REGISTERS_ACTIONS = {
    view: "registerDefinition:view",
    create: "registerDefinition:create",
    edit: "registerDefinition:edit",
    delete: "registerDefinition:delete",
} as const;

export type ConfigurationRegistersAction = NestedValues<typeof CONFIGURATION_REGISTERS_ACTIONS>;
