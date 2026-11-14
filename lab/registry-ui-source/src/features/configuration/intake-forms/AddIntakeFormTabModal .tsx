'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import {
    BaseModal,
    InputField,
} from '../shared/components';

interface AddIntakeFormTabModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    intakeFormId: string;
}

export default function AddIntakeFormTabModal({
    onClose,
    onSuccess,
    intakeFormId
}: AddIntakeFormTabModalProps) {
    const t = useTranslations();
    const { execute: createForm } = useFetch();

    const [formData, setFormData] = useState({
        tab_label: '',
        tab_order: 0
    });

    const handleSubmit = async () => {
        if (!formData.tab_label) {
            toast.error(t('please_fill_required_fields'));
            return;
        }

        const result = await createForm('/api/configuration/intake-forms/create-tab', {
            method: 'POST',
            body: JSON.stringify({
                form_id: intakeFormId,
                tab_label: formData.tab_label || null,
                tab_order: formData.tab_order,
            }),
        });

        if (result?.tab_id) {
            toast.success(t('toast_intake_form_tab_created'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_intake_form_tab_create_failed'));
        }
    };

    return (
        <BaseModal
            title={t('add_intake_form_tab')}
            onClose={onClose}
            primaryActionLabel={t('save')}
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
