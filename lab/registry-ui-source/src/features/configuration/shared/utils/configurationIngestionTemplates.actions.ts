import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_INGESTION_TEMPLATES_ACTIONS = {
    view: "ingestTemplate:view",
    create: "ingestTemplate:create",
    edit: "ingestTemplate:edit",
    delete: "ingestTemplate:delete",
} as const;

export type ConfigurationIngestionTemplatesAction = NestedValues<typeof CONFIGURATION_INGESTION_TEMPLATES_ACTIONS>;
