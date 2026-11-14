'use client';

import { useState, useRef } from 'react';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { BaseModal, FileUploadField } from '@/features/configuration/shared';
import { useDocumentUpload } from '@/features/register/hooks/useDocumentUpload';
import { useTranslations } from 'next-intl';

interface ImportModalProps {
    onClose: () => void;
    importFileConfig?: any;
}

export default function ImportModal({
    onClose,
    importFileConfig
}: ImportModalProps) {
    const t = useTranslations();

    const { execute } = useFetch();

    const { uploadDocument } = useDocumentUpload((url, options) =>
        execute(url, options)
    );

    const fileInputRef = useRef<HTMLInputElement>(null);

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploadedFileName, setUploadedFileName] = useState('');
    const [uploading, setUploading] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setSelectedFile(file);
        setUploadedFileName(file.name);
        e.target.value = '';
    };

    const handleRemoveFile = () => {
        setSelectedFile(null);
        setUploadedFileName('');
    };

    const handleImport = async () => {
        if (!selectedFile) {
            toast.warn(t('all_fields_are_required'));
            return;
        }

        try {
            setUploading(true);

            const uploadedDoc = await uploadDocument({
                file: selectedFile,
                label: 'import_file',
            });

            if (!uploadedDoc?.document_store_id) {
                toast.error(t('file_upload_failed'));
                return;
            }

            const result = await execute('/api/input-mechanism/enqueue-import', {
                method: 'POST',
                body: JSON.stringify({
                    document_store_id: uploadedDoc.document_store_id,
                    data_model_id: importFileConfig.data_model_id,
                    register_id: importFileConfig.register_id,
                    intake_form_id: importFileConfig.form_id,
                }),
            });

            if (result) {
                toast.success(t('import_successful'));
                onClose();
            } else {
                toast.error(t('import_failed'));
            }
        } catch (err) {
            toast.error(t('something_went_wrong'));
        } finally {
            setUploading(false);
        }
    };

    return (
        <BaseModal
            title={t('import_file')}
            onClose={onClose}
            primaryActionLabel={t('import')}
            onPrimaryAction={handleImport}
            maxWidth="max-w-150"
        >
            <FileUploadField
                label={t('upload_file')}
                fileInputRef={fileInputRef}
                uploading={uploading}
                fileName={uploadedFileName}
                fileId=""
                onFileChange={handleFileChange}
                onRemove={handleRemoveFile}
            />
        </BaseModal>
    );
}
