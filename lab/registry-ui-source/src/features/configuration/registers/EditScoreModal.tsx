'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import type { ScoreDefinition } from '../shared/types/registers';

interface EditScoreModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
    initialData?: ScoreDefinition | null;
}

export default function EditScoreModal({ isOpen, onClose, onSuccess, initialData }: EditScoreModalProps) {
    const t = useTranslations();
    const { execute: updateScore } = useFetch();

    const [isEnabled, setIsEnabled] = useState(() => initialData?.is_enabled ?? true);

    const handleSubmit = async () => {
        if (!initialData?.score_definition_id) return;

        const result = await updateScore('/api/configuration/registers/score/update-score-definitions', {
            method: 'POST',
            body: JSON.stringify({
                score_definition_id: initialData.score_definition_id,
                is_enabled: isEnabled,
            }),
        });

        const updated = result as { score_definition_id?: string; error?: string } | null;
        if (updated?.score_definition_id && !updated.error) {
            toast.success(t('toast_score_updated'));
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_score_update_failed'));
        }
    };

    const handleCancel = () => {
        onClose();
    };

    if (!isOpen || !initialData) return null;

    return (
        <div className="fixed inset-0 bg-neutral-first/80 z-50 flex items-center justify-center p-4">
            <div className="relative w-full max-w-200 max-h-150 bg-primary-first rounded-[10px] overflow-hidden flex p-1">
                <div className="flex-1 w-full bg-neutral-second p-10 relative rounded-[10px] overflow-y-auto">
                    <button
                        onClick={handleCancel}
                        className="absolute top-6 right-6 text-secondary-third hover:text-neutral-first/70 transition-colors"
                    >
                        <X size={40} strokeWidth={2} />
                    </button>

                    <h2 className="text-2xl font-bold text-primary-second mb-4">{t('edit_score')}</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-semibold text-neutral-first mb-2">
                                {t('score_type')}
                            </label>
                            <div className="w-full px-4 py-2 border border-secondary-first rounded-lg text-neutral-first/70 bg-secondary-second/25">
                                {initialData.score_type}
                            </div>
                        </div>

                        <div className="flex items-center gap-3 mt-2">
                            <input
                                type="checkbox"
                                id="score_is_enabled"
                                checked={isEnabled}
                                onChange={(e) => setIsEnabled(e.target.checked)}
                                className="h-4 w-4 rounded border-primary-second text-primary-second focus:ring-primary-second"
                            />
                            <label htmlFor="score_is_enabled" className="text-sm font-semibold text-neutral-first">
                                {t('status')}
                            </label>
                        </div>

                        <div className="flex gap-4 pt-6">
                            <button
                                onClick={handleCancel}
                                className="px-12 py-2.5 bg-secondary-third text-neutral-first rounded-[10px]"
                            >
                                {t('cancel')}
                            </button>
                            <button
                                onClick={handleSubmit}
                                className="px-12 py-2.5 bg-neutral-first text-neutral-second rounded-[10px]"
                            >
                                {t('save')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
