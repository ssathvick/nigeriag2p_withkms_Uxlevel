import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { useParams } from 'next/navigation';
import { toast } from 'react-toastify';
import { useAllRegisterSectionsBrief } from '../shared/hooks/useAllRegisterSectionsBrief';
import { BaseModal, CustomDropdown, InputField } from '../shared/components';




interface AddTabSectionModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddTabSectionModal({ onClose, onSuccess }: AddTabSectionModalProps) {
    const t = useTranslations();
    const { registerId, tabId } = useParams<{ registerId: string; tabId: string }>();
    const { execute: createSection } = useFetch();
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


    const handleSubmit = async () => {
        if (!formData.section_id) {
            toast.warn('Section Id is required');
            return;
        }

        const result = await createSection('/api/configuration/registers/tab-metadata/add-section', {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                tab_id: tabId,
                section_id: formData.section_id,
                section_order: Number(formData.section_order) || 0,
            })
        });


        if (result?.tab_section_id) {
            toast.success('Section created successfully');
            setFormData({
                section_id: '',
                section_order: 0
            });

            if (onSuccess) onSuccess();
            onClose();
        } else {
            toast.error('Failed to create section');
        }
    };

    const handleCancel = () => {
        setFormData({
            section_id: '',
            section_order: 0
        });

        onClose();
    };


    return (
        <BaseModal
            title={t('add_new_section')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-200"
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
