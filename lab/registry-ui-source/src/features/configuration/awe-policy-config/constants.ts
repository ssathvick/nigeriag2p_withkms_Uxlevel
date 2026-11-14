/** Mirrors backend `AwePolicyScopeEnum` (enum.py). */
export const AWE_POLICY_SCOPE_OPTIONS = [
    { value: 'REGISTER', labelKey: 'awe_policy_scope_register' },
    { value: 'INTAKE_FORM', labelKey: 'awe_policy_scope_intake_form' },
    { value: 'SECTION', labelKey: 'awe_policy_scope_section' },
] as const;

export type AwePolicyScope = (typeof AWE_POLICY_SCOPE_OPTIONS)[number]['value'];

/** Hardcoded policy types sent to the API. */
export const AWE_POLICY_TYPE_OPTIONS = [
    { value: 'registry.intake_form', labelKey: 'intake_form' },
    { value: 'registry.change_request', labelKey: 'change_request' },
] as const;

export type AwePolicyType = (typeof AWE_POLICY_TYPE_OPTIONS)[number]['value'];

export function getAwePolicyTypeLabelKey(policyType?: string | null): string | undefined {
    return AWE_POLICY_TYPE_OPTIONS.find((o) => o.value === policyType)?.labelKey;
}
