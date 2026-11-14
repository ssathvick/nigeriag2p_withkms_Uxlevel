'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useAllRegister } from '../shared';
import { useAllDataModels } from '../shared/hooks/useAllDataModels';
import CustomDropdown from '../shared/components/CustomDropdown';
import { BaseModal, InputField, TextAreaField } from '../shared/components';



interface EditOutgestionTopicModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    data?: any;
}

export default function EditOutgestionTopicModal({
    onClose,
    onSuccess,
    data,
}: EditOutgestionTopicModalProps) {
    const t = useTranslations();
    const { execute: updateOutgestionTemplate } = useFetch();
    const { config } = useRuntimeConfig();
    const currentPage = 1;

    const { registers, loading: registersLoading } = useAllRegister(currentPage, config.pageSize);
    const { dataModels, loading: dataModelsLoading } = useAllDataModels(currentPage, config.pageSize);

    const registerOptions =
        registers?.map((item: any) => ({
            label: t(item.register_subject),
            value: item.register_id,
        })) || [];

    const dataModelOptions =
        dataModels?.map((item: any) => ({
            label: item.data_model_mnemonic,
            value: item.data_model_id,
        })) || [];

    const [formData, setFormData] = useState({
        topic_id: '',
        register_id: '',
        data_model_id: '',
        websub_topic: '',
        description: ''
    });

    useEffect(() => {
        if (data) {
            setFormData({
                topic_id: data.topic_id || '',
                register_id: data.register_id || '',
                data_model_id: data.data_model_id || '',
                websub_topic: data.websub_topic || '',
                description: data.description || '',
            });
        }
    }, [data]);


    const handleSubmit = async () => {
        if (!formData.register_id || !formData.data_model_id) {
            toast.warn('Register Id & Data Model Id are required');
            return;
        }

        const result = await updateOutgestionTemplate(
            '/api/configuration/outgest/update-topic',
            {
                method: 'POST',
                body: JSON.stringify({
                    ...formData,
                    topic_id: data?.topic_id,
                }),
            }
        );

        if (result) {
            toast.success(t('topic_updated'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('topic_update_failed'));
        }
    };

    const handleCancel = () => {
        onClose();
    };

    return (
        <BaseModal
            title={t('edit_outgestion_topics')}
            onClose={handleCancel}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth='max-w-200'
        >
            <CustomDropdown
                label={t('register_id')}
                options={registerOptions}
                value={formData.register_id}
                loading={registersLoading}
                disabled={registersLoading}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        register_id: value,
                    }))
                }
            />

            <CustomDropdown
                label={t('data_model_id')}
                options={dataModelOptions}
                value={formData.data_model_id}
                loading={dataModelsLoading}
                disabled={dataModelsLoading}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        data_model_id: value,
                    }))
                }
            />

            <InputField
                label={t('websub_topic')}
                value={formData.websub_topic}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        websub_topic: value,
                    }))
                }
            />

            <TextAreaField
                label={t('description')}
                value={formData.description}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        description: value,
                    }))
                }
                rows={4}
            />
        </BaseModal>
    );
}
