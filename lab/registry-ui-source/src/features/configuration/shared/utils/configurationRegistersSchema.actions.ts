import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_REGISTERS_SCHEMA_ACTIONS = {
    filterSchemaView: "configurationRegistersFilterSchema.view",
    filterSchemaEdit: "configurationRegistersFilterSchema.edit",
    searchSchemaView: "configurationRegistersSearchSchema.view",
    searchSchemaEdit: "configurationRegistersSearchSchema.edit",
    deduplicationSchemaView: "configurationRegistersDeduplicationSchema.view",
    deduplicationSchemaEdit: "configurationRegistersDeduplicationSchema.edit",
} as const;

export type ConfigurationRegistersSchemaAction = NestedValues<typeof CONFIGURATION_REGISTERS_SCHEMA_ACTIONS>;
