'use client';

import { useMemo, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useAllDataModels, useAllIntakeForms } from '@/features/configuration/shared';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';

interface AddImportFileConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddImportFileConfigModal({
    isOpen,
    onClose,
    onSuccess,
}: AddImportFileConfigModalProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { execute: createConfig } = useFetch();
    const { intake_forms, loading: intakeFormsLoading } = useAllIntakeForms(1, 100, registerId);
    const { dataModels, loading: dataModelsLoading } = useAllDataModels(1, 100);

    const [formId, setFormId] = useState('');
    const [dataModelId, setDataModelId] = useState('');
    const [templateMnemonic, setTemplateMnemonic] = useState('');
    const [templateDescription, setTemplateDescription] = useState('');

    const formOptions = useMemo(
        () =>
            (intake_forms || []).map((form) => ({
                label: form.form_mnemonic || form.form_description || form.form_id,
                value: form.form_id,
            })),
        [intake_forms],
    );

    const dataModelOptions = useMemo(
        () =>
            (dataModels || []).map((model) => ({
                label: model.data_model_mnemonic || model.data_model_id,
                value: model.data_model_id,
            })),
        [dataModels],
    );

    const resetForm = () => {
        setFormId('');
        setDataModelId('');
        setTemplateMnemonic('');
        setTemplateDescription('');
    };

    const handleCancel = () => {
        resetForm();
        onClose();
    };

    const handleSubmit = async () => {
        if (!formId) {
            toast.warn(t('form_id_required'));
            return;
        }
        if (!dataModelId) {
            toast.warn(t('data_model_id_required'));
            return;
        }
        if (!templateMnemonic.trim()) {
            toast.warn(t('template_mnemonic_required'));
            return;
        }

        const result = await createConfig(
            '/api/input-mechanism/create-import-file-configuration',
            {
                method: 'POST',
                body: JSON.stringify({
                    register_id: registerId,
                    form_id: formId,
                    data_model_id: dataModelId,
                    import_file_template_mnemonic: templateMnemonic.trim(),
                    import_file_template_description: templateDescription.trim(),
                }),
            },
        );

        if (result?.import_file_configuration_id) {
            toast.success(t('toast_import_file_config_created'));
            resetForm();
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_import_file_config_create_failed'));
        }
    };

    if (!isOpen) return null;

    return (
        <BaseModal
            title={t('add_import_file_config')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
        >
            <div className="space-y-4">
                <CustomDropdown
                    label={t('form_id')}
                    options={formOptions}
                    value={formId}
                    onChange={setFormId}
                    loading={intakeFormsLoading}
                    placeholder={t('select_intake_form')}
                />
                <CustomDropdown
                    label={t('data_model_mnemonic')}
                    options={dataModelOptions}
                    value={dataModelId}
                    onChange={setDataModelId}
                    loading={dataModelsLoading}
                    placeholder={t('select_data_model')}
                />
                <InputField
                    label={t('template_mnemonic')}
                    value={templateMnemonic}
                    onChange={setTemplateMnemonic}
                    placeholder={t('enter_template_mnemonic')}
                />
                <TextAreaField
                    label={t('template_description')}
                    value={templateDescription}
                    onChange={setTemplateDescription}
                    placeholder={t('enter_template_description')}
                />
            </div>
        </BaseModal>
    );
}
