import { NestedValues } from "@/shared/types/types";

export const INTAKE_FORM_ACTIONS = {
    view: "intakeSubmission:view",
    approve: "intakeSubmission:approve",
    edit: "intakeSubmission:edit"
} as const;

export type IntakeFormAction = NestedValues<typeof INTAKE_FORM_ACTIONS>;
