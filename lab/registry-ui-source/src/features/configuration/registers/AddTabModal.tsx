import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { useParams } from 'next/navigation';
import { toast } from 'react-toastify';
import { BaseModal, InputField } from '../shared/components';

interface AddTabModalProps {
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddTabModal({ onClose, onSuccess }: AddTabModalProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { execute: createTab, loading } = useFetch();

    const [formData, setFormData] = useState({
        tab_label: '',
        tab_order: '',
    });

    const handleSubmit = async () => {
        if (!formData.tab_label) {
            toast.warn('Tab Name is required');
            return;
        }

        const result = await createTab('/api/configuration/registers/tab-metadata/create-tab', {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                tab_label: formData.tab_label,
                tab_order: Number(formData.tab_order) || 0,
                is_active: true
            })
        });

        if (result?.tab_id) {
            toast.success('Tab created successfully');
            setFormData({ tab_label: '', tab_order: '' });
            if (onSuccess) onSuccess();
            onClose();
        } else {
            toast.error('Failed to create tab');
        }
    };

    const handleCancel = () => {
        setFormData({
            tab_label: '',
            tab_order: '',
        });
        onClose();
    };


    return (
        <BaseModal
            title={t('add_new_tab')}
            onClose={handleCancel}
            primaryActionLabel={t('save')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-200"
        >
            <InputField
                label={t('tab_name')}
                placeholder={t('enter_tab_label')}
                value={formData.tab_label}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, tab_label: value }))
                }
            />
            <InputField
                label={t('tab_order')}
                type="number"
                placeholder="e.g. 0, 1, 2, etc."
                value={formData.tab_order}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, tab_order: value }))
                }
            />
        </BaseModal>
    );
}
