'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { IncomingSemanticPattern } from '@/features/configuration/shared/hooks/useAllSemanticPatterns';
import { useAllRegister, useRegisterSections, useAllDataModels } from '@/features/configuration/shared';
import { BaseModal, InputField, CustomDropdown, TextAreaField } from '../shared/components';
import { useIntakeForms } from '@/features/intake-form/hooks/useIntakeForms';

interface EditSemanticPatternModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: IncomingSemanticPattern;
}

export default function EditSemanticPatternModal({
    onClose,
    onSuccess,
    initialData
}: EditSemanticPatternModalProps) {
    const t = useTranslations();
    const { execute: updatePattern } = useFetch();
    const { registers } = useAllRegister(1, 100);
    const { dataModels } = useAllDataModels(1, 100);

    const [formData, setFormData] = useState({
        data_model_id: '',
        data_model_mnemonic: '',
        register_id: '',
        register_mnemonic: '',
        intake_form_id: '',
        intake_form_mnemonic: '',
        pattern_for_register: '',
        pattern_for_intake_form: '',
        key_path_for_business_payload: '',
        raw_payload_enricher_class: '',
    });

    // const { sections, loading: loadingSections } = useRegisterSections(formData.register_id);
    const { forms, loading: formsLoading } = useIntakeForms(formData.register_id);

    useEffect(() => {
        if (initialData) {
            setFormData({
                data_model_id: initialData.data_model_id || '',
                data_model_mnemonic: initialData.data_model_mnemonic || '',
                register_id: initialData.register_id || '',
                register_mnemonic: initialData.register_mnemonic || '',
                intake_form_id: initialData.intake_form_id || '',
                intake_form_mnemonic: initialData.intake_form_mnemonic || '',
                pattern_for_register: initialData.pattern_for_register || '',
                pattern_for_intake_form: initialData.pattern_for_intake_form || '',
                key_path_for_business_payload: initialData.key_path_for_business_payload || '',
                raw_payload_enricher_class: initialData.raw_payload_enricher_class || '',
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!initialData?.semantic_pattern_id) return;

        const result = await updatePattern('/api/configuration/ingest/update-semantic-pattern', {
            method: 'POST',
            body: JSON.stringify({
                semantic_pattern_id: initialData.semantic_pattern_id,
                data_model_id: formData.data_model_id,
                register_id: formData.register_id,
                intake_form_id: formData.intake_form_id || null,
                pattern_for_register: formData.pattern_for_register,
                pattern_for_intake_form: formData.pattern_for_intake_form,
                key_path_for_business_payload: formData.key_path_for_business_payload,
                raw_payload_enricher_class: formData.raw_payload_enricher_class,
            })
        });

        if (result?.semantic_pattern_id) {
            toast.success(t('toast_semantic_pattern_updated'));
            if (onSuccess) onSuccess();
            onClose();
        } else {
            toast.error(t('toast_semantic_pattern_update_failed'));
        }
    };

    const handleCancel = () => {
        onClose();
    };

    return (
        <BaseModal
            title={t('edit_semantic_pattern')}
            onClose={handleCancel}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth='max-w-220'
        >
            <CustomDropdown
                label={t('data_model_mnemonic')}
                options={dataModels.map((dm) => ({
                    label: dm.data_model_mnemonic,
                    value: dm.data_model_id,
                }))}
                value={formData.data_model_id}
                onChange={(value) => {
                    const mnemonic = dataModels.find(dm => dm.data_model_id === value)?.data_model_mnemonic || '';
                    setFormData((prev) => ({ ...prev, data_model_id: value, data_model_mnemonic: mnemonic }))
                }}
            />

            <CustomDropdown
                label={t('register_mnemonic')}
                options={registers.map((r) => ({
                    label: r.register_mnemonic,
                    value: r.register_id,
                }))}
                value={formData.register_id}
                onChange={(value) => {
                    const mnemonic = registers.find(r => r.register_id === value)?.register_mnemonic || '';
                    setFormData((prev) => ({ ...prev, register_id: value, register_mnemonic: mnemonic }))
                }}
            />

            <CustomDropdown
                label={t('intake_form_mnemonic')}
                options={forms.map((f) => ({
                    label: f.form_mnemonic,
                    value: f.form_id,
                }))}
                value={formData.intake_form_id}
                loading={formsLoading}
                disabled={!formData.register_id}
                onChange={(value) => {
                    const mnemonic =
                        forms.find(f => f.form_id === value)?.form_mnemonic || '';

                    setFormData(prev => ({
                        ...prev,
                        intake_form_id: value,
                        intake_form_mnemonic: mnemonic
                    }));
                }}
            />

            <TextAreaField
                label={t('pattern_for_register')}
                value={formData.pattern_for_register}
                textareaClassName="h-16"
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        pattern_for_register: value,
                    }))
                }
            />

            <TextAreaField
                label={t('pattern_for_intake_form')}
                value={formData.pattern_for_intake_form}
                textareaClassName="h-16"
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        pattern_for_intake_form: value,
                    }))
                }
            />

            <TextAreaField
                label={t('key_path_for_business_payload')}
                value={formData.key_path_for_business_payload}
                textareaClassName="h-32"
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        key_path_for_business_payload: value,
                    }))
                }
            />

            <InputField
                label={t('raw_payload_enricher_class')}
                value={formData.raw_payload_enricher_class}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        raw_payload_enricher_class: value,
                    }))
                }
            />
        </BaseModal>
    );
}
