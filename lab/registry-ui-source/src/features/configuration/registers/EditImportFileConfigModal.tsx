'use client';

import { useEffect, useMemo, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useAllDataModels, useAllIntakeForms } from '@/features/configuration/shared';
import type { ImportFileConfiguration } from '@/features/configuration/shared/hooks/useAllImportFileConfigurations';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';

interface EditImportFileConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: ImportFileConfiguration | null;
}

export default function EditImportFileConfigModal({
    isOpen,
    onClose,
    onSuccess,
    initialData,
}: EditImportFileConfigModalProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { execute: updateConfig } = useFetch();
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

    useEffect(() => {
        if (initialData) {
            setFormId(initialData.form_id ?? '');
            setDataModelId(initialData.data_model_id ?? '');
            setTemplateMnemonic(initialData.import_file_template_mnemonic ?? '');
            setTemplateDescription(initialData.import_file_template_description ?? '');
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!initialData?.import_file_configuration_id) return;
        if (!formId || !dataModelId || !templateMnemonic.trim()) {
            toast.warn(t('toast_operation_failed'));
            return;
        }

        const result = await updateConfig(
            '/api/input-mechanism/update-import-file-configuration',
            {
                method: 'POST',
                body: JSON.stringify({
                    import_file_configuration_id: initialData.import_file_configuration_id,
                    register_id: registerId,
                    form_id: formId,
                    data_model_id: dataModelId,
                    import_file_template_mnemonic: templateMnemonic.trim(),
                    import_file_template_description: templateDescription.trim(),
                }),
            },
        );

        if (result?.import_file_configuration_id) {
            toast.success(t('toast_import_file_config_updated'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_import_file_config_update_failed'));
        }
    };

    if (!isOpen || !initialData) return null;

    return (
        <BaseModal
            title={t('edit_import_file_config')}
            onClose={onClose}
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
                />
                <TextAreaField
                    label={t('template_description')}
                    value={templateDescription}
                    onChange={setTemplateDescription}
                />
            </div>
        </BaseModal>
    );
}
