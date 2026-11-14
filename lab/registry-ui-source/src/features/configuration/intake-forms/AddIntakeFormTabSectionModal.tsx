'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import {
    BaseModal,
    CustomDropdown,
    InputField,
} from '../shared/components';
import { useAllRegister } from '../shared/hooks/useAllRegister';
import { useAllRegisterSectionsBrief } from '../shared/hooks/useAllRegisterSectionsBrief';

interface AddIntakeFormTabSectionModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    tabId: string;
}

export default function AddIntakeFormTabSectionModal({
    onClose,
    onSuccess,
    tabId
}: AddIntakeFormTabSectionModalProps) {
    const t = useTranslations();
    const { execute: createForm } = useFetch();

    const [formData, setFormData] = useState({
        register_id: '',
        section_id: '',
        section_order: 0
    });

    const { registers, loading: registerLoading } = useAllRegister(1, 100);
    const { sections, loading: sectionLoading } = useAllRegisterSectionsBrief(formData.register_id, 1, 100);

    const registerOptions =
        registers?.map((reg: any) => ({
            label: reg.register_mnemonic,
            value: reg.register_id,
        })) || [];

    const sectionOptions =
        sections?.map((sec: any) => ({
            label: sec.section_mnemonic,
            value: sec.section_id,
        })) || [];

    const handleSubmit = async () => {
        if (!formData.section_id || !formData.section_order) {
            toast.error(t('please_fill_required_fields'));
            return;
        }

        const result = await createForm('/api/configuration/intake-forms/create-section', {
            method: 'POST',
            body: JSON.stringify({
                tab_id: tabId,
                section_id: formData.section_id || null,
                section_order: formData.section_order,
            }),
        });

        if (result?.tab_section_id) {
            toast.success(t('toast_intake_form_tab_section_created'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_intake_form_tab_section_create_failed'));
        }
    };

    return (
        <BaseModal
            title={t('add_intake_form_tab_section')}
            onClose={onClose}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >

            <CustomDropdown
                label={t('register')}
                options={registerOptions}
                value={formData.register_id}
                loading={registerLoading}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        register_id: value,
                        section_id: ''
                    }))
                }
            />

            <CustomDropdown
                label={t('section')}
                options={sectionOptions}
                value={formData.section_id}
                loading={sectionLoading}
                onChange={(value) =>
                    setFormData((prev) => ({
                        ...prev,
                        section_id: value,
                    }))
                }
            />

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
