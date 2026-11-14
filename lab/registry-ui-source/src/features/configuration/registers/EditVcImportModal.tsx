'use client';

import { useEffect, useMemo, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useAllDataModels, useAllIntakeForms } from '@/features/configuration/shared';
import type { VcImport } from '@/features/configuration/shared/hooks/useAllVcImports';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';

interface EditVcImportModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: VcImport | null;
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

export default function EditVcImportModal({
    isOpen,
    onClose,
    onSuccess,
    initialData,
}: EditVcImportModalProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { execute: updateConfig } = useFetch();
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

    useEffect(() => {
        if (initialData) {
            setIntakeFormId(initialData.intake_form_id ?? '');
            setDataModelId(initialData.data_model_id ?? '');
            setVcMnemonic(initialData.vc_mnemonic ?? '');
            setDescriptorSchemaJson(
                JSON.stringify(initialData.descriptor_schema ?? {}, null, 2),
            );
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!initialData?.vc_config_id) return;
        if (!intakeFormId || !dataModelId || !vcMnemonic.trim()) {
            toast.warn(t('toast_operation_failed'));
            return;
        }

        const descriptorSchema = parseDescriptorSchema(descriptorSchemaJson);
        if (descriptorSchema === null) {
            toast.error(t('invalid_descriptor_schema_json'));
            return;
        }

        const result = await updateConfig('/api/input-mechanism/update-vc-configuration', {
            method: 'POST',
            body: JSON.stringify({
                vc_config_id: initialData.vc_config_id,
                register_id: registerId,
                intake_form_id: intakeFormId,
                data_model_id: dataModelId,
                vc_mnemonic: vcMnemonic.trim(),
                descriptor_schema: descriptorSchema,
            }),
        });

        if (result?.vc_config_id) {
            toast.success(t('toast_vc_import_updated'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_vc_import_update_failed'));
        }
    };

    if (!isOpen || !initialData) return null;

    return (
        <BaseModal
            title={t('edit_vc_import')}
            onClose={onClose}
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
                />
                <TextAreaField
                    label={t('descriptor_schema')}
                    value={descriptorSchemaJson}
                    onChange={setDescriptorSchemaJson}
                />
            </div>
        </BaseModal>
    );
}
