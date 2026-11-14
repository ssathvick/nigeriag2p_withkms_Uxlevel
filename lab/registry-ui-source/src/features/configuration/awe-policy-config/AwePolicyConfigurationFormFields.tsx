'use client';

import { useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { CustomDropdown, InputField, TextAreaField } from '../shared/components';
import { useAllRegister } from '../shared/hooks/useAllRegister';
import { useAllRegisterSectionsBrief } from '../shared/hooks/useAllRegisterSectionsBrief';
import { useIntakeForms } from '@/features/intake-form/hooks/useIntakeForms';
import {
    AWE_POLICY_SCOPE_OPTIONS,
    AWE_POLICY_TYPE_OPTIONS,
    type AwePolicyScope,
} from './constants';
import type { AwePolicyFormState } from './scopePayload';

export type { AwePolicyFormState };

interface Props {
    formData: AwePolicyFormState;
    setFormData: React.Dispatch<React.SetStateAction<AwePolicyFormState>>;
}

export default function AwePolicyConfigurationFormFields({ formData, setFormData }: Props) {
    const t = useTranslations();
    const { registers, loading: loadingRegisters } = useAllRegister(1, 100);
    const { forms, loading: loadingForms } = useIntakeForms(formData.register_id || undefined);
    const { sections, loading: loadingSections } = useAllRegisterSectionsBrief(
        formData.register_id || undefined,
        1,
        100
    );

    const scopeOptions = AWE_POLICY_SCOPE_OPTIONS.map((opt) => ({
        label: t(opt.labelKey),
        value: opt.value,
    }));

    const policyTypeOptions = AWE_POLICY_TYPE_OPTIONS.map((opt) => ({
        label: t(opt.labelKey),
        value: opt.value,
    }));

    const showIntakeForm = formData.policy_scope === 'INTAKE_FORM';
    const showSection = formData.policy_scope === 'SECTION';

    const registerOptions = useMemo(() => {
        const purposeRegisters = registers.filter(
            (r) => r.register_purpose === 'REGISTER',
        );
        const selectedId = formData.register_id;
        if (
            selectedId &&
            !purposeRegisters.some((r) => r.register_id === selectedId)
        ) {
            const selected = registers.find((r) => r.register_id === selectedId);
            if (selected) {
                purposeRegisters.push(selected);
            }
        }
        return purposeRegisters.map((r) => ({
            label: r.register_mnemonic,
            value: r.register_id,
        }));
    }, [registers, formData.register_id]);

    return (
        <>
            <CustomDropdown
                label={t('policy_scope')}
                options={scopeOptions}
                value={formData.policy_scope}
                onChange={(value) => {
                    const scope = value as AwePolicyScope;
                    setFormData((prev) => ({
                        ...prev,
                        policy_scope: scope,
                        intake_form_id: scope === 'INTAKE_FORM' ? prev.intake_form_id : '',
                        section_id: scope === 'SECTION' ? prev.section_id : '',
                    }));
                }}
            />

            <CustomDropdown
                label={t('register_mnemonic')}
                options={registerOptions}
                loading={loadingRegisters}
                value={formData.register_id}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        register_id: value,
                        intake_form_id: '',
                        section_id: '',
                    }))
                }
            />

            {showIntakeForm && (
                <CustomDropdown
                    label={t('intake_form_mnemonic')}
                    options={forms.map((f) => ({
                        label: f.form_mnemonic,
                        value: f.form_id,
                    }))}
                    loading={loadingForms}
                    disabled={!formData.register_id}
                    value={formData.intake_form_id}
                    onChange={(value) =>
                        setFormData((prev) => ({ ...prev, intake_form_id: value }))
                    }
                />
            )}

            {showSection && (
                <CustomDropdown
                    label={t('section_mnemonic')}
                    options={(sections || []).map((s: { section_id: string; section_mnemonic: string }) => ({
                        label: s.section_mnemonic,
                        value: s.section_id,
                    }))}
                    loading={loadingSections}
                    disabled={!formData.register_id}
                    value={formData.section_id}
                    onChange={(value) =>
                        setFormData((prev) => ({ ...prev, section_id: value }))
                    }
                />
            )}

            <CustomDropdown
                label={t('policy_type')}
                options={policyTypeOptions}
                value={formData.policy_type}
                onChange={(value) =>
                    setFormData((prev) => ({ ...prev, policy_type: value }))
                }
            />

            <InputField
                label={t('policy_key')}
                value={formData.policy_key}
                onChange={(value) =>
                    setFormData((prev) => ({ ...prev, policy_key: value }))
                }
            />

            <TextAreaField
                label={t('context_field_names')}
                value={formData.context_field_names}
                onChange={(value) =>
                    setFormData((prev) => ({ ...prev, context_field_names: value }))
                }
                rows={2}
            />
        </>
    );
}

export {
    buildScopePayload,
    formatContextFieldNames,
    parseContextFieldNames,
} from './scopePayload';
