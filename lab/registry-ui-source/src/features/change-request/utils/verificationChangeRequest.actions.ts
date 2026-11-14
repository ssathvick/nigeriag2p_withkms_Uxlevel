import { NestedValues } from "@/shared/types/types";

export const VERIFICATION_CHANGE_REQUEST_ACTIONS = {
    view: "verificationChangeRequest:view",
    create: "verificationChangeRequest:create"
} as const;

export type VerificationChangeRequestAction = NestedValues<typeof VERIFICATION_CHANGE_REQUEST_ACTIONS>;
