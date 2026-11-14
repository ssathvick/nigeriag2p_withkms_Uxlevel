'use client';

import { useState, useEffect, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useFileUpload } from '../shared/hooks/useFileUpload';
import { BaseModal, Field, FileUploadField } from '../shared/components';

interface EditOutgestionTemplateModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    data?: any;
}

export default function EditOutgestionTemplateModal({
    onClose,
    onSuccess,
    data,
}: EditOutgestionTemplateModalProps) {
    const t = useTranslations();
    const { execute: updateOutgestionTemplate } = useFetch();

    const fileInputRef = useRef<HTMLInputElement>(null);

    const [formData, setFormData] = useState({
        template_id: '',
        template_file_id: '',
    });

    useEffect(() => {
        if (data) {
            setFormData({
                template_id: data.template_id || '',
                template_file_id: data.template_file_id || '',
            });
        }
    }, [data]);

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const { uploadFile, uploading, uploadedFileName, setUploadedFileName } = useFileUpload("/api/configuration/outgest/upload-template");

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
        const result = await updateOutgestionTemplate(
            '/api/configuration/outgest/update-template',
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
            toast.success(t('outgest_template_updated'));
            setFormData({
                template_id: '',
                template_file_id: '',
            });
            setUploadedFileName('');
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('outgest_template_update_failed'));
        }
    };

    const handleCancel = () => {
        onClose();
    };

    return (
        <BaseModal
            title={t('edit_outgestion_templates')}
            onClose={handleCancel}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth='max-w-200'
        >
            <FileUploadField
                label={t('template_id')}
                fileInputRef={fileInputRef}
                uploading={uploading}
                fileId={formData.template_file_id}
                fileName={uploadedFileName}
                onFileChange={handleFileChange}
                onRemove={handleRemoveFile}
            />
        </BaseModal>
    );
}
