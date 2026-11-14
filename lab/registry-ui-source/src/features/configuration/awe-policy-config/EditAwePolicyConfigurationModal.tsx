'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { BaseModal } from '../shared/components';
import type { AwePolicyConfiguration } from '../shared/hooks/useAllAwePolicyConfigurations';
import AwePolicyConfigurationFormFields, {
    buildScopePayload,
    formatContextFieldNames,
    type AwePolicyFormState,
} from './AwePolicyConfigurationFormFields';
import type { AwePolicyScope } from './constants';

interface Props {
    data?: AwePolicyConfiguration | null;
    onClose: () => void;
    onSuccess?: () => void;
}

export default function EditAwePolicyConfigurationModal({ data, onClose, onSuccess }: Props) {
    const t = useTranslations();
    const { execute: updateConfig } = useFetch();
    const [formData, setFormData] = useState<AwePolicyFormState>({
        policy_scope: '',
        register_id: '',
        intake_form_id: '',
        section_id: '',
        policy_type: '',
        policy_key: '',
        context_field_names: '',
    });

    useEffect(() => {
        if (!data) return;
        const scope = data.policy_scope as AwePolicyScope;
        setFormData({
            policy_scope: scope,
            register_id: data.register_id || '',
            intake_form_id:
                scope === 'INTAKE_FORM' ? data.intake_form_id || '' : '',
            section_id: scope === 'SECTION' ? data.section_id || '' : '',
            policy_type: data.policy_type || '',
            policy_key: data.policy_key || '',
            context_field_names: formatContextFieldNames(data.context_field_names),
        });
    }, [data]);

    const handleSubmit = async () => {
        if (
            !formData.policy_scope ||
            !formData.register_id ||
            !formData.policy_type ||
            !formData.policy_key
        ) {
            toast.warn(t('please_fill_required_fields'));
            return;
        }

        if (formData.policy_scope === 'INTAKE_FORM' && !formData.intake_form_id) {
            toast.warn(t('intake_form_required_for_scope'));
            return;
        }

        if (formData.policy_scope === 'SECTION' && !formData.section_id) {
            toast.warn(t('section_required_for_scope'));
            return;
        }

        const result = await updateConfig('/api/configuration/awe-policy-config/update', {
            method: 'POST',
            body: JSON.stringify({
                awe_policy_config_id: data?.awe_policy_config_id,
                ...buildScopePayload(formData),
            }),
        });

        if (result?.awe_policy_config_id) {
            toast.success(t('awe_policy_configuration_updated_successfully'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('failed_to_update_awe_policy_configuration'));
        }
    };

    return (
        <BaseModal
            title={t('edit_awe_policy_configuration')}
            onClose={onClose}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >
            <AwePolicyConfigurationFormFields formData={formData} setFormData={setFormData} />
        </BaseModal>
    );
}
