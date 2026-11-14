'use client';

import { useState } from 'react';
import { useRef } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useFileUpload } from '../shared/hooks/useFileUpload';
import { BaseModal, InputField, FileUploadField, CheckboxField, TextAreaField } from '../shared/components';


interface AddDataModelModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddDataModelModal({
    onClose,
    onSuccess,
}: AddDataModelModalProps) {
    const t = useTranslations();
    const { execute: createDataModel, loading } = useFetch();

    const fileInputRef = useRef<HTMLInputElement>(null);

    const [formData, setFormData] = useState({
        data_model_mnemonic: '',
        pattern_for_data_model: '',
        response_template_file_id: '',
        is_active: true,
    });

    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const { uploadFile, uploading, uploadedFileName, setUploadedFileName } = useFileUpload("/api/configuration/data-models/template-upload");

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setSelectedFile(file);
        setUploadedFileName(file.name)
        e.target.value = '';
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
        setUploadedFileName('');
    };

    const handleSubmit = async () => {
        if (!formData.data_model_mnemonic || !formData.pattern_for_data_model) {
            toast.warn('Mnemonic & Pattern are required');
            return;
        }

        let documentId = formData.response_template_file_id;
        if (selectedFile) {
            documentId = await uploadFile(selectedFile);
        }

        const result = await createDataModel(
            '/api/configuration/data-models/create',
            {
                method: 'POST',
                body: JSON.stringify({
                    ...formData,
                    response_template_file_id: documentId,
                }),
            }
        );

        if (result?.data_model_id) {
            toast.success(t('data_model_created_successfully'));

            setFormData({
                data_model_mnemonic: '',
                pattern_for_data_model: '',
                response_template_file_id: '',
                is_active: true,
            });

            onSuccess?.();
            onClose();
        } else {
            toast.error(t('failed_to_create_data_model'));
        }
    };

    const handleCancel = () => {
        setFormData({
            data_model_mnemonic: '',
            pattern_for_data_model: '',
            response_template_file_id: '',
            is_active: true,
        });
        onClose();
    };

    return (
        <BaseModal
            title={t('add_new_data_model')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-200"
        >
            <InputField
                label={t('data_model_mnemonic')}
                value={formData.data_model_mnemonic}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        data_model_mnemonic: value,
                    }))
                }
            />

            <TextAreaField
                label={t('pattern')}
                value={formData.pattern_for_data_model}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        pattern_for_data_model: value,
                    }))
                }
                rows={1}
            />

            <div className="grid grid-cols-2 gap-6">
                <FileUploadField
                    label={t('template_id')}
                    fileInputRef={fileInputRef}
                    uploading={uploading}
                    fileId={formData.response_template_file_id}
                    fileName={uploadedFileName}
                    onFileChange={handleFileChange}
                    onRemove={handleRemoveFile}
                />

                {/* <CheckboxField
                    label={t('status')}
                    checked={formData.is_active}
                    onChange={(value) =>
                        setFormData((prev) => ({
                            ...prev,
                            is_active: value,
                        }))
                    }
                /> */}
            </div>
        </BaseModal>
    );
}
