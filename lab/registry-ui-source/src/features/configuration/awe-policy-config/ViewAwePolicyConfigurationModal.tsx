'use client';

import { useTranslations } from 'next-intl';
import { BaseModal, Field } from '../shared/components';
import type { AwePolicyConfiguration } from '../shared/hooks/useAllAwePolicyConfigurations';
import { AWE_POLICY_SCOPE_OPTIONS, getAwePolicyTypeLabelKey } from './constants';
import { formatContextFieldNames } from './AwePolicyConfigurationFormFields';

interface Props {
    data?: AwePolicyConfiguration | null;
    onClose: () => void;
    registerLabel?: string;
}

export default function ViewAwePolicyConfigurationModal({
    data,
    onClose,
    registerLabel,
}: Props) {
    const t = useTranslations();

    const scopeLabel =
        AWE_POLICY_SCOPE_OPTIONS.find((o) => o.value === data?.policy_scope)?.labelKey;

    const policyTypeLabelKey = getAwePolicyTypeLabelKey(data?.policy_type);

    return (
        <BaseModal title={t('view_awe_policy_configuration')} onClose={onClose} maxWidth="max-w-220">
            <div className="bg-secondary-second/50 px-8 pt-2 pb-4">
                <Field
                    label={t('policy_scope')}
                    value={scopeLabel ? t(scopeLabel) : data?.policy_scope}
                />
                <Field label={t('register_mnemonic')} value={registerLabel ?? data?.register_id} />
                {data?.intake_form_id && (
                    <Field label={t('intake_form_mnemonic')} value={data.intake_form_id} />
                )}
                {data?.section_id && (
                    <Field label={t('section_mnemonic')} value={data.section_id} />
                )}
                <Field
                    label={t('policy_type')}
                    value={
                        policyTypeLabelKey
                            ? t(policyTypeLabelKey)
                            : data?.policy_type
                    }
                />
                <Field label={t('policy_key')} value={data?.policy_key} />
                <Field
                    label={t('context_field_names')}
                    value={formatContextFieldNames(data?.context_field_names)}
                />
            </div>
        </BaseModal>
    );
}
