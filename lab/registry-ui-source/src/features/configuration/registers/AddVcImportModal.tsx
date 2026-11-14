'use client';

import { useMemo, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useAllDataModels, useAllIntakeForms } from '@/features/configuration/shared';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';

interface AddVcImportModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

function parseDescriptorSchema(raw: string): Record<string, unknown> | null {
    const trimmed = raw.trim();
    if (!trimmed) return {};
    try {
        const parsed = JSON.parse(trimmed) as unknown;
        if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
            return null;
        }
        return parsed as Record<string, unknown>;
    } catch {
        return null;
    }
}

export default function AddVcImportModal({ isOpen, onClose, onSuccess }: AddVcImportModalProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { execute: createConfig } = useFetch();
    const { intake_forms, loading: intakeFormsLoading } = useAllIntakeForms(1, 100, registerId);
    const { dataModels, loading: dataModelsLoading } = useAllDataModels(1, 100);

    const [intakeFormId, setIntakeFormId] = useState('');
    const [dataModelId, setDataModelId] = useState('');
    const [vcMnemonic, setVcMnemonic] = useState('');
    const [descriptorSchemaJson, setDescriptorSchemaJson] = useState('{}');

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
        setIntakeFormId('');
        setDataModelId('');
        setVcMnemonic('');
        setDescriptorSchemaJson('{}');
    };

    const handleCancel = () => {
        resetForm();
        onClose();
    };

    const handleSubmit = async () => {
        if (!intakeFormId) {
            toast.warn(t('form_id_required'));
            return;
        }
        if (!dataModelId) {
            toast.warn(t('data_model_id_required'));
            return;
        }
        if (!vcMnemonic.trim()) {
            toast.warn(t('vc_mnemonic_required'));
            return;
        }

        const descriptorSchema = parseDescriptorSchema(descriptorSchemaJson);
        if (descriptorSchema === null) {
            toast.error(t('invalid_descriptor_schema_json'));
            return;
        }

        const result = await createConfig('/api/input-mechanism/create-vc-configuration', {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                intake_form_id: intakeFormId,
                data_model_id: dataModelId,
                vc_mnemonic: vcMnemonic.trim(),
                descriptor_schema: descriptorSchema,
            }),
        });

        if (result?.vc_config_id) {
            toast.success(t('toast_vc_import_created'));
            resetForm();
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_vc_import_create_failed'));
        }
    };

    if (!isOpen) return null;

    return (
        <BaseModal
            title={t('add_vc_import')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
        >
            <div className="space-y-4">
                <CustomDropdown
                    label={t('form_id')}
                    options={formOptions}
                    value={intakeFormId}
                    onChange={setIntakeFormId}
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
                    label={t('vc_mnemonic')}
                    value={vcMnemonic}
                    onChange={setVcMnemonic}
                    placeholder={t('enter_vc_mnemonic')}
                />
                <TextAreaField
                    label={t('descriptor_schema')}
                    value={descriptorSchemaJson}
                    onChange={setDescriptorSchemaJson}
                    placeholder="{}"
                />
            </div>
        </BaseModal>
    );
}
