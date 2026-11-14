'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import {
    BaseModal,
    InputField,
} from '../shared/components';

interface EditIntakeFormTabSectionModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: any;
}

export default function EditIntakeFormTabSectionModal({
    onClose,
    onSuccess,
    initialData
}: EditIntakeFormTabSectionModalProps) {
    const t = useTranslations();
    const { execute: updateForm } = useFetch();

    const [formData, setFormData] = useState({
        section_order: 0,
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                section_order: initialData.section_order,
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!initialData?.tab_section_id) return;

        const result = await updateForm('/api/configuration/intake-forms/update-section', {
            method: 'POST',
            body: JSON.stringify({
                tab_section_id: initialData.tab_section_id,
                section_order: Number(formData.section_order),
            }),
        });

        if (result?.tab_section_id) {
            toast.success(t('toast_intake_form_tab_section_updated'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_intake_form_tab_section_update_failed'));
        }
    };

    return (
        <BaseModal
            title={t('edit_intake_form_tab_section')}
            onClose={onClose}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >
            <InputField
                label={t('section_order')}
                type="number"
                value={formData.section_order}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        section_order: Number(value),
                    }))
                }
            />
        </BaseModal>
    );
}
