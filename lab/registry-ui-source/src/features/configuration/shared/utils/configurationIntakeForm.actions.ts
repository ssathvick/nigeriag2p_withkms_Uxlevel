import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_INTAKE_FORM_ACTIONS = {
    view: "intakeFormDefinition:view",
    // create: "intakeFormDefinition:create",
    edit: "intakeFormDefinition:edit",
    // delete: "intakeFormDefinition:delete",
} as const;

export type ConfigurationIntakeFormAction = NestedValues<typeof CONFIGURATION_INTAKE_FORM_ACTIONS>;
