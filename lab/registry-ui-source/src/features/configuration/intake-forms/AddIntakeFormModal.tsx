'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import {
    BaseModal,
    InputField,
    TextAreaField,
    CustomDropdown,
} from '../shared/components';
import { useAllRegister } from '../shared/hooks/useAllRegister';

interface AddIntakeFormModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddIntakeFormModal({
    onClose,
    onSuccess,
}: AddIntakeFormModalProps) {
    const t = useTranslations();
    const { execute: createForm } = useFetch();
    const { registers, loading: registerLoading } = useAllRegister(1, 100);

    const registerOptions =
        registers?.map((reg: any) => ({
            label: reg.register_mnemonic,
            value: reg.register_id,
        })) || [];

    const [formData, setFormData] = useState({
        form_mnemonic: '',
        form_description: '',
        register_id: '',
        number_of_verifications: 0,
    });

    const handleSubmit = async () => {
        if (!formData.form_mnemonic || !formData.register_id) {
            toast.error(t('please_fill_required_fields'));
            return;
        }

        const result = await createForm('/api/configuration/intake-forms/create-intake-form', {
            method: 'POST',
            body: JSON.stringify({
                form_mnemonic: formData.form_mnemonic,
                form_description: formData.form_description || null,
                register_id: formData.register_id,
                number_of_verifications: Number(formData.number_of_verifications),
            }),
        });

        if (result?.form_id) {
            toast.success(t('toast_intake_form_created'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_intake_form_create_failed'));
        }
    };

    return (
        <BaseModal
            title={t('add_intake_form')}
            onClose={onClose}
            primaryActionLabel={t('save')}
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

            <div className="grid grid-cols-2 gap-4">
                <CustomDropdown
                    label={t('register')}
                    options={registerOptions}
                    value={formData.register_id}
                    loading={registerLoading}
                    onChange={(value) =>
                        setFormData((prev) => ({
                            ...prev,
                            register_id: value,
                        }))
                    }
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
            </div>
        </BaseModal>
    );
}
