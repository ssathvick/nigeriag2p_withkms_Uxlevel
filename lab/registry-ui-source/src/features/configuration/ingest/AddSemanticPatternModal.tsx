'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useAllRegister, useRegisterSections, useAllDataModels } from '@/features/configuration/shared';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';
import { useIntakeForms } from '@/features/intake-form/hooks/useIntakeForms';

interface AddSemanticPatternModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddSemanticPatternModal({ onClose, onSuccess }: AddSemanticPatternModalProps) {
    const t = useTranslations();
    const { execute: createPattern } = useFetch();
    const { registers, loading: loadingRegisters } = useAllRegister(1, 100);
    const { dataModels, loading: loadingDataModels } = useAllDataModels(1, 100);

    const [formData, setFormData] = useState({
        data_model_id: '',
        data_model_mnemonic: '',
        register_id: '',
        register_mnemonic: '',
        intake_form_id: '',
        section_mnemonic: '',
        pattern_for_register: '',
        pattern_for_intake_form: '',
        key_path_for_business_payload: '',
        raw_payload_enricher_class: '',
    });

    // const { sections, loading: loadingSections } = useRegisterSections(formData.register_id);
    const { forms, loading: formsLoading } = useIntakeForms(formData.register_id);

    useEffect(() => {
        setFormData(prev => ({ ...prev, section_id: '', section_mnemonic: '' }));
    }, [formData.register_id]);

    const handleSubmit = async () => {
        if (!formData.data_model_id || !formData.register_id) {
            toast.warn(t('data_model') + ' and ' + t('register') + ' are required');
            return;
        }

        const result = await createPattern('/api/configuration/ingest/create-semantic-pattern', {
            method: 'POST',
            body: JSON.stringify({
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
            toast.success(t('toast_semantic_pattern_created'));
            resetForm();
            if (onSuccess) onSuccess();
            onClose();
        } else {
            toast.error(t('toast_semantic_pattern_create_failed'));
        }
    };

    const resetForm = () => {
        setFormData({
            data_model_id: '',
            data_model_mnemonic: '',
            register_id: '',
            register_mnemonic: '',
            intake_form_id: '',
            section_mnemonic: '',
            pattern_for_register: '',
            pattern_for_intake_form: '',
            key_path_for_business_payload: '',
            raw_payload_enricher_class: '',
        });
    };

    const handleCancel = () => {
        resetForm();
        onClose();
    };

    return (
        <BaseModal
            title={t('add_new_semantic_pattern')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth='max-w-220'
        >
            <CustomDropdown
                label={t('data_model_mnemonic')}
                options={dataModels.map(dm => ({
                    label: dm.data_model_mnemonic,
                    value: dm.data_model_id,
                }))}
                loading={loadingDataModels}
                value={formData.data_model_id}
                onChange={(value) => {
                    const mnemonic = dataModels.find(dm => dm.data_model_id === value)?.data_model_mnemonic || '';
                    setFormData(prev => ({ ...prev, data_model_id: value, data_model_mnemonic: mnemonic }))
                }}
            />

            <CustomDropdown
                label={t('register_mnemonic')}
                options={registers.map(r => ({
                    label: r.register_mnemonic,
                    value: r.register_id,
                }))}
                loading={loadingRegisters}
                value={formData.register_id}
                onChange={(value) => {
                    const mnemonic = registers.find(r => r.register_id === value)?.register_mnemonic || '';
                    setFormData(prev => ({ ...prev, register_id: value, register_mnemonic: mnemonic }))
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
                    setFormData(prev => ({ ...prev, pattern_for_register: value }))
                }
                rows={2}
            />

            <TextAreaField
                label={t('pattern_for_intake_form')}
                value={formData.pattern_for_intake_form}
                textareaClassName="h-16"
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, pattern_for_intake_form: value }))
                }
                rows={2}
            />

            <TextAreaField
                label={t('key_path_for_business_payload')}
                value={formData.key_path_for_business_payload}
                textareaClassName="h-32"
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        key_path_for_business_payload: value
                    }))
                }
            />

            <InputField
                label={t('raw_payload_enricher_class')}
                value={formData.raw_payload_enricher_class}
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        raw_payload_enricher_class: value
                    }))
                }
            />
        </BaseModal>
    );
}
