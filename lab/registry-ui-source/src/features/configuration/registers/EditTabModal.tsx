import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { Tab } from '../shared/types';
import { BaseModal, InputField } from '../shared/components';
import CheckboxField from '../shared/components/CheckboxField';

interface EditTabModalProps {
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: Tab;
    registerId: string;
}

export default function EditTabModal({ onClose, onSuccess, initialData, registerId }: EditTabModalProps) {
    const t = useTranslations();
    const { execute: updateTab, loading } = useFetch();

    const [formData, setFormData] = useState({
        tab_label: '',
        tab_order: '',
        is_active: true
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                tab_label: initialData.tab_label || '',
                tab_order: initialData.tab_order?.toString() || '0',
                is_active: initialData.is_active || true
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!formData.tab_label) {
            toast.warn('Tab Label is required');
            return;
        }

        const result = await updateTab('/api/configuration/registers/tab-metadata/update-tab', {
            method: 'POST',
            body: JSON.stringify({
                tab_id: initialData?.tab_id,
                tab_label: formData.tab_label,
                tab_order: Number(formData.tab_order) || 0,
                is_active: formData.is_active || true
            })
        });

        if (result) {
            toast.success(`Tab "${formData.tab_label}" updated successfully`);
            if (onSuccess) onSuccess();
            onClose();
        } else {
            toast.error('Failed to update tab');
        }
    };

    const handleCancel = () => {
        onClose();
    };

    return (
        <BaseModal
            title={t('edit_tab')}
            onClose={handleCancel}
            primaryActionLabel={t('update')}
            onPrimaryAction={handleSubmit}
            maxWidth="max-w-200"
        >
            <InputField
                label={t('tab_label')}
                placeholder={t('enter_tab_label')}
                value={formData.tab_label}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, tab_label: value }))
                }
            />
            <InputField
                label={t('tab_order')}
                type="number"
                placeholder="e.g. 0"
                value={formData.tab_order}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, tab_order: value }))
                }
            />
            <CheckboxField
                label={t('is_active')}
                checked={formData.is_active}
                onChange={(value) =>
                    setFormData(prev => ({ ...prev, is_active: value }))
                }
            />
        </BaseModal>
    );
}
