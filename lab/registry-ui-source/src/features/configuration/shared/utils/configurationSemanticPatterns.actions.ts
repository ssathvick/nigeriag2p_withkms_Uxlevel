import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS = {
    view: "ingestExpression:view",
    create: "ingestExpression:create",
    edit: "ingestExpression:edit",
} as const;

export type ConfigurationSemanticPatternsAction = NestedValues<typeof CONFIGURATION_SEMANTIC_PATTERNS_ACTIONS>;
