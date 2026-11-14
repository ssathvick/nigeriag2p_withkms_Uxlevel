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

interface EditIntakeFormTabModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: any;
}

export default function EditIntakeFormTabModal({
    onClose,
    onSuccess,
    initialData
}: EditIntakeFormTabModalProps) {
    const t = useTranslations();
    const { execute: updateForm } = useFetch();

    const [formData, setFormData] = useState({
        tab_label: '',
        tab_order: 0,
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                tab_label: initialData.tab_label || '',
                tab_order: initialData.tab_order,
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!initialData?.tab_id) return;

        const result = await updateForm('/api/configuration/intake-forms/update-tab', {
            method: 'POST',
            body: JSON.stringify({
                tab_id: initialData.tab_id,
                tab_label: formData.tab_label,
                tab_order: Number(formData.tab_order),
            }),
        });

        if (result?.tab_id) {
            toast.success(t('toast_intake_form_tab_updated'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_intake_form_tab_update_failed'));
        }
    };

    return (
        <BaseModal
            title={t('edit_intake_form_tab')}
            onClose={onClose}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >
            <InputField
                label={t('tab_label')}
                value={formData.tab_label}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        tab_label: value,
                    }))
                }
            />

            <InputField
                label={t('tab_order')}
                type="number"
                value={formData.tab_order}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        tab_order: Number(value),
                    }))
                }
            />
        </BaseModal>
    );
}
