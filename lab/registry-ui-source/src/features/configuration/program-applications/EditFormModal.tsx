'use client';

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { Tab } from '../shared/types';

interface EditFormModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    initialData: Tab;
    registerId: string;
}

export default function EditFormModal({ isOpen, onClose, onSuccess, initialData, registerId }: EditFormModalProps) {
    const t = useTranslations();
    const { execute: updateForm, loading } = useFetch();
    const [formData, setFormData] = useState({
        tab_label: '',
        tab_order: 0,
    });

    useEffect(() => {
        if (initialData) {
            setFormData({
                tab_label: initialData.tab_label || '',
                tab_order: initialData.tab_order || 0,
            });
        }
    }, [initialData]);

    const handleSubmit = async () => {
        if (!formData.tab_label) {
            toast.warn('Form Label is required');
            return;
        }

        const result = await updateForm('/api/configuration/registers/tabs/edit', {
            method: 'POST',
            body: JSON.stringify({
                tab_id: initialData.tab_id,
                register_id: registerId,
                tab_label: formData.tab_label,
                tab_order: Number(formData.tab_order),
            })
        });

        if (result) {
            toast.success(t('toast_form_updated'));
            onSuccess();
            onClose();
        } else {
            toast.error(t('toast_form_update_failed'));
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-neutral-first/80 z-50 flex items-center justify-center p-4">
            <div className="relative w-full max-w-200 bg-primary-first rounded-[10px] p-1">
                <div className="bg-neutral-second rounded-[10px] p-10 relative">
                    <button onClick={onClose} className="absolute top-6 right-6 text-secondary-third hover:text-neutral-first/70">
                        <X size={40} />
                    </button>

                    <h2 className="text-2xl font-bold text-primary-second mb-6">{t('edit_form')}</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-semibold text-neutral-first mb-1">{t('form_label')}</label>
                            <input
                                type="text"
                                value={formData.tab_label}
                                onChange={(e) => setFormData({ ...formData, tab_label: e.target.value })}
                                className="w-full px-4 py-2 border border-primary-second rounded-lg outline-none"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-neutral-first mb-1">{t('form_order')}</label>
                            <input
                                type="number"
                                value={formData.tab_order}
                                onChange={(e) => setFormData({ ...formData, tab_order: Number(e.target.value) })}
                                className="w-full px-4 py-2 border border-primary-second rounded-lg outline-none"
                            />
                        </div>

                        <div className="flex gap-4 pt-6">
                            <button onClick={onClose} className="px-12 py-2.5 bg-secondary-third text-neutral-first rounded-[10px]">{t('cancel')}</button>
                            <button onClick={handleSubmit} disabled={loading} className="px-12 py-2.5 bg-neutral-first text-neutral-second rounded-[10px]">{t('save_changes')}</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
