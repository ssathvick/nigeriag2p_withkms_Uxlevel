import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_REGISTRY_ACTIONS = {
    view: "registryConfiguration:view",
    edit: "registryConfiguration:edit",
} as const;

export type ConfigurationRegistryAction = NestedValues<typeof CONFIGURATION_REGISTRY_ACTIONS>;
