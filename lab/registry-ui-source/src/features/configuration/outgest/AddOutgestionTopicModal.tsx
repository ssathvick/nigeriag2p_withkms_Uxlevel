'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useAllRegister } from '../shared';
import { useAllDataModels } from '../shared/hooks/useAllDataModels';
import CustomDropdown from '../shared/components/CustomDropdown';
import { BaseModal, InputField, TextAreaField } from '../shared/components';


interface AddOutgestionTopicModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddOutgestionTopicModal({
    onClose,
    onSuccess,
}: AddOutgestionTopicModalProps) {
    const t = useTranslations();
    const { execute: createOutgestionTopic, loading } = useFetch();
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
        register_id: '',
        data_model_id: '',
        websub_topic: '',
        description: ''
    });


    const handleSubmit = async () => {
        if (!formData.register_id || !formData.data_model_id) {
            toast.warn('Register Id & Data Model Id are required');
            return;
        }

        const result = await createOutgestionTopic(
            '/api/configuration/outgest/create-topic',
            {
                method: 'POST',
                body: JSON.stringify(formData),
            }
        );

        if (result.topic_id) {
            toast.success(t('topic_created'));

            setFormData({
                register_id: '',
                data_model_id: '',
                websub_topic: '',
                description: ''
            });

            onSuccess?.();
            onClose();
        } else {
            toast.error(t('topic_creation_failed'));
        }
    };

    const handleCancel = () => {
        setFormData({
            register_id: '',
            data_model_id: '',
            websub_topic: '',
            description: ''
        });
        onClose();
    };

    return (
        <BaseModal
            title={t('add_new_outgestion_topic')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth='max-w-200'
        >
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
        </BaseModal >
    );
}
