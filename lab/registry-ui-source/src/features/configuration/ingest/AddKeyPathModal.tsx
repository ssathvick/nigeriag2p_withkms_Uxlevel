'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useAllDataModels } from '@/features/configuration/shared';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';

interface AddKeyPathModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddKeyPathModal({ onClose, onSuccess }: AddKeyPathModalProps) {
    const t = useTranslations();
    const { execute: createKeyPath } = useFetch();
    const { dataModels, loading: dataModelsLoading } = useAllDataModels(1, 100);

    const dataModelOptions =
        dataModels?.map((dm) => ({
            label: dm.data_model_mnemonic,
            value: dm.data_model_id,
        })) || [];

    const [formData, setFormData] = useState({
        data_model_id: '',
        key_path_for_message_id: '',
        key_path_for_sender: '',
        key_path_for_signature: '',
        key_path_for_signature_payload: '',
        is_list: false,
        key_path_for_list_elements: '',
    });

    const handleSubmit = async () => {
        if (!formData.data_model_id) {
            toast.warn(t('data_model_id') + ' is required');
            return;
        }

        const result = await createKeyPath('/api/configuration/ingest/create-key-path', {
            method: 'POST',
            body: JSON.stringify({
                data_model_id: formData.data_model_id,
                key_path_for_message_id: formData.key_path_for_message_id || null,
                key_path_for_sender: formData.key_path_for_sender || null,
                key_path_for_signature: formData.key_path_for_signature || null,
                key_path_for_signature_payload: formData.key_path_for_signature_payload || null,
                is_list: formData.is_list,
                key_path_for_list_elements: formData.key_path_for_list_elements || null,
            })
        });

        if (result?.key_path_id) {
            toast.success(t('toast_key_path_created'));
            resetForm();
            if (onSuccess) onSuccess();
            onClose();
        } else {
            toast.error(t('toast_key_path_create_failed'));
        }
    };

    const resetForm = () => {
        setFormData({
            data_model_id: '',
            key_path_for_message_id: '',
            key_path_for_sender: '',
            key_path_for_signature: '',
            key_path_for_signature_payload: '',
            is_list: false,
            key_path_for_list_elements: '',
        });
    };

    const handleCancel = () => {
        resetForm();
        onClose();
    };

    return (
        <BaseModal
            title={t('add_new_key_path')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth='max-w-220'
        >
            <CustomDropdown
                label={t('data_model_mnemonic')}
                options={dataModelOptions}
                value={formData.data_model_id}
                loading={dataModelsLoading}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        data_model_id: value,
                    }))
                }
            />

            <TextAreaField
                label={t('key_path_for_message_id')}
                value={formData.key_path_for_message_id}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        key_path_for_message_id: value,
                    }))
                }
                rows={1}
            />

            <TextAreaField
                label={t('key_path_for_sender')}
                value={formData.key_path_for_sender}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        key_path_for_sender: value,
                    }))
                }
                rows={1}
            />

            <CustomDropdown
                label={t('is_list')}
                options={[
                    { label: t('true'), value: 'true' },
                    { label: t('false'), value: 'false' },
                ]}
                value={formData.is_list ? 'true' : 'false'}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        is_list: value === 'true',
                    }))
                }
            />

            {formData.is_list && (
                <TextAreaField
                    label={t('key_pat_for_list_elements')}
                    value={formData.key_path_for_list_elements}
                    onChange={(value) =>
                        setFormData((prev) => ({
                            ...prev,
                            key_path_for_list_elements: value,
                        }))
                    }
                    rows={3}
                />
            )}

            <TextAreaField
                label={t('key_path_for_signature')}
                value={formData.key_path_for_signature}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        key_path_for_signature: value,
                    }))
                }
                rows={1}
            />

            <TextAreaField
                label={t('key_path_for_signature_payload')}
                value={formData.key_path_for_signature_payload}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        key_path_for_signature_payload: value,
                    }))
                }
                rows={1}
            />
        </BaseModal>
    );
}
