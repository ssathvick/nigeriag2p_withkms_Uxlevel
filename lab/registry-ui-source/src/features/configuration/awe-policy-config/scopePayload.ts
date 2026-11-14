import type { AwePolicyScope } from './constants';

export type AwePolicyFormState = {
    policy_scope: AwePolicyScope | '';
    register_id: string;
    intake_form_id: string;
    section_id: string;
    policy_type: string;
    policy_key: string;
    context_field_names: string;
};

export function parseContextFieldNames(raw: string): string[] | null {
    const trimmed = raw.trim();
    if (!trimmed) return null;
    return trimmed
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
}

export function formatContextFieldNames(names?: string[] | null): string {
    if (!names?.length) return '';
    return names.join(', ');
}

/** Empty string clears optional ids on update (null means "unchanged" in backend). */
export function scopeScopedIds(body: {
    policy_scope?: string;
    intake_form_id?: string | null;
    section_id?: string | null;
}) {
    const scope = body.policy_scope;
    if (scope === 'REGISTER') {
        return { intake_form_id: '', section_id: '' };
    }
    if (scope === 'INTAKE_FORM') {
        return {
            intake_form_id: body.intake_form_id ?? '',
            section_id: '',
        };
    }
    if (scope === 'SECTION') {
        return {
            intake_form_id: '',
            section_id: body.section_id ?? '',
        };
    }
    return {
        intake_form_id: body.intake_form_id ?? '',
        section_id: body.section_id ?? '',
    };
}

export function buildScopePayload(formData: AwePolicyFormState) {
    return {
        policy_scope: formData.policy_scope,
        register_id: formData.register_id,
        policy_type: formData.policy_type,
        policy_key: formData.policy_key,
        context_field_names: parseContextFieldNames(formData.context_field_names),
        ...scopeScopedIds(formData),
    };
}
