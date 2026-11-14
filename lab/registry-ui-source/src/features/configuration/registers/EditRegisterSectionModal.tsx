'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { useParams } from 'next/navigation';
import { toast } from 'react-toastify';
import { BaseModal, CustomDropdown, InputField, TextAreaField } from '../shared/components';
import CheckboxField from '../shared/components/CheckboxField';
import { Section } from '../shared/types';
import { useAllRegister } from '../shared/hooks/useAllRegister';

interface EditRegisterSectionModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: Section;
}

export default function EditRegisterSectionModal({
    onClose,
    onSuccess,
    initialData
}: EditRegisterSectionModalProps) {

    const t = useTranslations();
    const { sectionId } = useParams<{
        sectionId: string;
    }>();

    const { registers, loading: loadingRegisters } = useAllRegister(1, 100);

    const { execute: updateSection } = useFetch();

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
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                section_register_id: initialData.section_register_id || '',
                section_mnemonic: initialData.section_mnemonic || '',
                section_description: initialData.section_description || '',
                section_weightage: initialData.section_weightage || 0,
                documents_required: !!initialData.documents_required,
                no_of_verifications_required: initialData.no_of_verifications_required || 0,
                cr_auto_approve_for_bene_portal: initialData.cr_auto_approve_for_bene_portal || false,
                cr_auto_approve_for_agent_portal: initialData.cr_auto_approve_for_agent_portal || false,
                cr_auto_approve_for_staff_portal: initialData.cr_auto_approve_for_staff_portal || false,
                cr_auto_approve_for_partner: initialData.cr_auto_approve_for_partner || false,
                is_list: !!initialData.is_list,
                is_core_section: !!initialData.is_core_section,
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!formData.section_mnemonic) {
            toast.warn(t('section_mnemonic_required'));
            return;
        }

        const result = await updateSection(
            '/api/configuration/registers/section-metadata/update-section',
            {
                method: 'POST',
                body: JSON.stringify({
                    section_id: sectionId,
                    ...formData,
                })
            }
        );

        if (result) {
            toast.success(t('section_updated_successfully'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('section_update_failed'));
        }
    };

    return (
        <BaseModal
            title={t('edit_section')}
            onClose={onClose}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-220"
        >
            <InputField
                label={t('section_mnemonic')}
                value={formData.section_mnemonic}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, section_mnemonic: value }))
                }
            />

            <TextAreaField
                label={t('section_description')}
                value={formData.section_description}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, section_description: value }))
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

            <InputField
                label={t('no_of_verifications_required')}
                type="number"
                value={String(formData.no_of_verifications_required)}
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        no_of_verifications_required: Number(value) || 0
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
