import { NestedValues } from "@/shared/types/types";

export const VERIFICATION_INTAKE_FORM_ACTIONS = {
    view: "verificationIntakeForm:view",
    create: "verificationIntakeForm:create"
} as const;

export type VerificationIntakeFormAction = NestedValues<typeof VERIFICATION_INTAKE_FORM_ACTIONS>;
