'use client';

import { useState, useEffect, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useFileUpload } from '../shared/hooks/useFileUpload';
import { BaseModal, Field, FileUploadField, CheckboxField } from '../shared/components';


interface EditIngestionTemplateModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    data?: any;
}

export default function EditIngestionTemplateModal({
    onClose,
    onSuccess,
    data,
}: EditIngestionTemplateModalProps) {
    const t = useTranslations();
    const { execute: updateIngestionTemplate } = useFetch();

    const fileInputRef = useRef<HTMLInputElement>(null);

    const [formData, setFormData] = useState({
        template_id: '',
        template_file_id: '',
        jsonld_expansion_required: false
    });

    useEffect(() => {
        if (data) {
            setFormData({
                template_id: data.template_id || '',
                template_file_id: data.template_file_id || '',
                jsonld_expansion_required: data.jsonld_expansion_required || false
            });
        }
    }, [data]);

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const { uploadFile, uploading, uploadedFileName, setUploadedFileName } = useFileUpload("/api/configuration/ingest/upload-template");

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

        let documentId = formData.template_file_id;
        if (selectedFile) {
            documentId = await uploadFile(selectedFile);
        }
        const result = await updateIngestionTemplate(
            '/api/configuration/ingest/update-template',
            {
                method: 'POST',
                body: JSON.stringify({
                    ...formData,
                    template_id: data?.template_id,
                    template_file_id: documentId
                }),
            }
        );

        if (result) {
            toast.success(t('ingest_template_updated'));
            setFormData({
                template_id: '',
                template_file_id: '',
                jsonld_expansion_required: false
            });
            setUploadedFileName('');
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('ingest_template_update_failed'));
        }
    };

    const handleCancel = () => {
        onClose();
    };

    return (
        <BaseModal
            title={t('edit_ingestion_templates')}
            onClose={handleCancel}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth='max-w-200'
        >
            <Field label={t('register_mnemonic')} value={data.register_mnemonic} />
            <Field label={t('data_model_mnemonic')} value={data.data_model_mnemonic} />
            <div className="flex gap-6">
                <div className="flex-1">
                    <FileUploadField
                        label={t('template_id')}
                        fileInputRef={fileInputRef}
                        uploading={uploading}
                        fileId={formData.template_file_id}
                        fileName={uploadedFileName}
                        onFileChange={handleFileChange}
                        onRemove={handleRemoveFile}
                    />
                </div>

                <div className="flex-1">
                    <CheckboxField
                        label={t('jsonld_expansion')}
                        checked={formData.jsonld_expansion_required}
                        onChange={(value) =>
                            setFormData((prev) => ({
                                ...prev,
                                jsonld_expansion_required: value,
                            }))
                        }
                    />
                </div>
            </div>
        </BaseModal>
    );
}
