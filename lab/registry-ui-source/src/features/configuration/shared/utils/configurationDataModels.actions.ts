import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_DATA_MODELS_ACTIONS = {
    view: "dataModel:view",
    create: "dataModel:create",
    edit: "dataModel:edit",
    delete: "dataModel:delete",
} as const;

export type ConfigurationDataModelsAction = NestedValues<typeof CONFIGURATION_DATA_MODELS_ACTIONS>;
