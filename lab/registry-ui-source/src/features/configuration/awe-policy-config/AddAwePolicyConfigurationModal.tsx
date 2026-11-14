'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { BaseModal } from '../shared/components';
import AwePolicyConfigurationFormFields, {
    buildScopePayload,
    type AwePolicyFormState,
} from './AwePolicyConfigurationFormFields';

interface Props {
    onClose: () => void;
    onSuccess?: () => void;
}

const emptyForm: AwePolicyFormState = {
    policy_scope: '',
    register_id: '',
    intake_form_id: '',
    section_id: '',
    policy_type: '',
    policy_key: '',
    context_field_names: '',
};

export default function AddAwePolicyConfigurationModal({ onClose, onSuccess }: Props) {
    const t = useTranslations();
    const { execute: createConfig } = useFetch();
    const [formData, setFormData] = useState<AwePolicyFormState>(emptyForm);

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

        const result = await createConfig('/api/configuration/awe-policy-config/create', {
            method: 'POST',
            body: JSON.stringify(buildScopePayload(formData)),
        });

        if (result?.awe_policy_config_id) {
            toast.success(t('awe_policy_configuration_created_successfully'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('failed_to_create_awe_policy_configuration'));
        }
    };

    return (
        <BaseModal
            title={t('add_new_awe_policy_configuration')}
            onClose={onClose}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >
            <AwePolicyConfigurationFormFields formData={formData} setFormData={setFormData} />
        </BaseModal>
    );
}
