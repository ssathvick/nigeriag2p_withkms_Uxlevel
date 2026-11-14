'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { useParams } from 'next/navigation';
import { toast } from 'react-toastify';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';
import CheckboxField from '../shared/components/CheckboxField';
import { useAllRegister } from '../shared/hooks/useAllRegister';

interface AddRegisterSectionModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddRegisterSectionModal({
    onClose,
    onSuccess
}: AddRegisterSectionModalProps) {

    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { execute: createSection, loading } = useFetch();
    const { registers, loading: loadingRegisters } = useAllRegister(1, 100);


    const [formData, setFormData] = useState({
        section_register_id: '',
        section_mnemonic: '',
        section_description: '',
        section_weightage: 0,
        documents_required: false,
        no_of_verifications_required: 0,
        cr_auto_approve_for_bene_portal: false,
        cr_auto_approve_for_agent_portal: false,
        cr_auto_approve_for_staff_portal: false,
        cr_auto_approve_for_partner: false,
        is_list: false,
        is_core_section: false,
        section_ui_schema: {}
    });

    const resetForm = () => {
        setFormData({
            section_register_id: '',
            section_mnemonic: '',
            section_description: '',
            section_weightage: 0,
            documents_required: false,
            no_of_verifications_required: 0,
            cr_auto_approve_for_bene_portal: false,
            cr_auto_approve_for_agent_portal: false,
            cr_auto_approve_for_staff_portal: false,
            cr_auto_approve_for_partner: false,
            is_list: false,
            is_core_section: false,
            section_ui_schema: {}
        });
    };

    const handleSubmit = async () => {
        if (!formData.section_mnemonic) {
            toast.warn(t('section_mnemonic_required'));
            return;
        }

        const result = await createSection(
            '/api/configuration/registers/section-metadata/create-section',
            {
                method: 'POST',
                body: JSON.stringify({
                    ...formData,
                    register_id: registerId,
                })
            }
        );

        if (result) {
            toast.success(t('section_created_successfully'));
            resetForm();
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('section_create_failed'));
        }
    };

    const handleCancel = () => {
        resetForm();
        onClose();
    };

    return (
        <BaseModal
            title={t('add_new_section')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >
            <InputField
                label={t('section_mnemonic')}
                value={formData.section_mnemonic}
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        section_mnemonic: value
                    }))
                }
            />

            <TextAreaField
                label={t('section_description')}
                value={formData.section_description}
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        section_description: value
                    }))
                }
                rows={2}
            />

            <CustomDropdown
                label={t('section_register')}
                options={registers.map(r => ({
                    label: r.register_mnemonic,
                    value: r.register_id,
                }))}
                loading={loadingRegisters}
                value={formData.section_register_id}
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        section_register_id: value
                    }))
                }
            />

            <InputField
                label={t('section_weightage')}
                type="number"
                value={String(formData.section_weightage)}
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        section_weightage: Number(value) || 0
                    }))
                }
            />

            <div className="grid grid-cols-2 gap-4 pt-2">
                <CheckboxField
                    label={t('is_core_section')}
                    checked={formData.is_core_section}
                    onChange={(value) =>
                        setFormData(prev => ({
                            ...prev,
                            is_core_section: value
                        }))
                    }
                />

                <CheckboxField
                    label={t('cr_auto_approve_for_bene_portal')}
                    checked={formData.cr_auto_approve_for_bene_portal}
                    onChange={(value) =>
                        setFormData(prev => ({
                            ...prev,
                            cr_auto_approve_for_bene_portal: value
                        }))
                    }
                />

                <CheckboxField
                    label={t('is_list')}
                    checked={formData.is_list}
                    onChange={(value) =>
                        setFormData(prev => ({
                            ...prev,
                            is_list: value
                        }))
                    }
                />

                <CheckboxField
                    label={t('cr_auto_approve_for_agent_portal')}
                    checked={formData.cr_auto_approve_for_agent_portal}
                    onChange={(value) =>
                        setFormData(prev => ({
                            ...prev,
                            cr_auto_approve_for_agent_portal: value
                        }))
                    }
                />

                <CheckboxField
                    label={t('documents_required')}
                    checked={formData.documents_required}
                    onChange={(value) =>
                        setFormData(prev => ({
                            ...prev,
                            documents_required: value
                        }))
                    }
                />

                <CheckboxField
                    label={t('cr_auto_approve_for_staff_portal')}
                    checked={formData.cr_auto_approve_for_staff_portal}
                    onChange={(value) =>
                        setFormData(prev => ({
                            ...prev,
                            cr_auto_approve_for_staff_portal: value
                        }))
                    }
                />

                <CheckboxField
                    label={t('cr_auto_approve_for_partner')}
                    checked={formData.cr_auto_approve_for_partner}
                    onChange={(value) =>
                        setFormData(prev => ({
                            ...prev,
                            cr_auto_approve_for_partner: value
                        }))
                    }
                />
            </div>
        </BaseModal>
    );
}
