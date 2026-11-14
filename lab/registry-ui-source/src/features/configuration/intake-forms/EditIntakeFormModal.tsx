'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import {
    BaseModal,
    InputField,
    TextAreaField
} from '../shared/components';

interface EditIntakeFormModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: any;
}

export default function EditIntakeFormModal({
    onClose,
    onSuccess,
    initialData
}: EditIntakeFormModalProps) {
    const t = useTranslations();
    const { execute: updateForm } = useFetch();

    const [formData, setFormData] = useState({
        form_mnemonic: '',
        form_description: '',
        number_of_verifications: 0,
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                form_mnemonic: initialData.form_mnemonic || '',
                form_description: initialData.form_description || '',
                number_of_verifications: initialData.number_of_verifications || 0,
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!initialData?.form_id) return;

        const result = await updateForm('/api/configuration/intake-forms/update-intake-form', {
            method: 'POST',
            body: JSON.stringify({
                form_id: initialData.form_id,
                form_mnemonic: formData.form_mnemonic,
                form_description: formData.form_description,
                number_of_verifications: Number(formData.number_of_verifications),
            }),
        });

        if (result?.form_id) {
            toast.success(t('toast_intake_form_updated'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_intake_form_update_failed'));
        }
    };

    return (
        <BaseModal
            title={t('edit_intake_form')}
            onClose={onClose}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >
            <InputField
                label={t('form_mnemonic')}
                value={formData.form_mnemonic}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        form_mnemonic: value,
                    }))
                }
            />

            <TextAreaField
                label={t('description')}
                value={formData.form_description}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        form_description: value,
                    }))
                }
                rows={2}
            />

            <InputField
                label={t('number_of_verifications')}
                type="number"
                value={formData.number_of_verifications}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        number_of_verifications: Number(value),
                    }))
                }
            />
        </BaseModal>
    );
}
