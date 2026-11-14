import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { useParams } from 'next/navigation';
import { toast } from 'react-toastify';
import { useAllRegisterSectionsBrief } from '../shared/hooks/useAllRegisterSectionsBrief';
import { BaseModal, CustomDropdown, InputField } from '../shared/components';


interface EditTabSectionModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: any;
}

export default function EditTabSectionModal({
    onClose,
    onSuccess,
    initialData
}: EditTabSectionModalProps) {

    const t = useTranslations();
    const { registerId, tabId } = useParams<{ registerId: string; tabId: string }>();
    const { execute: updateSection } = useFetch();
    const { sections } = useAllRegisterSectionsBrief(registerId, 1, 100);

    const sectionOptions =
        sections?.map((sec: any) => ({
            label: sec.section_mnemonic,
            value: sec.section_id,
        })) || [];

    const [formData, setFormData] = useState({
        section_id: '',
        section_order: 0
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                section_id: initialData.section_id,
                section_order: initialData.section_order
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!formData.section_id) {
            toast.warn('Section Id is required');
            return;
        }

        const result = await updateSection(
            '/api/configuration/registers/tab-metadata/update-section',
            {
                method: 'POST',
                body: JSON.stringify({
                    tab_section_id: initialData?.tab_section_id,
                    section_id: formData.section_id,
                    section_order: Number(formData.section_order) || 0,
                })
            }
        );

        if (result) {
            toast.success('Section updated successfully');
            onSuccess?.();
            onClose();
        } else {
            toast.error('Failed to update section');
        }
    };

    const handleCancel = () => {
        onClose();
    };

    return (
        <BaseModal
            title={t('edit_tab_section')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
        >
            <CustomDropdown
                label={t('section')}
                value={formData.section_id}
                placeholder={t('select_section')}
                options={sectionOptions}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, section_id: value }))
                }
            />
            <InputField
                label={t('section_order')}
                type="number"
                placeholder="e.g. 0"
                value={formData.section_order}
                onChange={(value) =>
                    setFormData(prev => ({
                        ...prev,
                        section_order: Number(value) || 0
                    }))
                }
            />
        </BaseModal>
    );
}
