'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';
import { useParams } from 'next/navigation';
import { toast } from 'react-toastify';

interface AddScoreModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: () => void;
}

export default function AddScoreModal({ isOpen, onClose, onSuccess }: AddScoreModalProps) {
    const t = useTranslations();
    const { registerId } = useParams<{ registerId: string }>();
    const { execute: createScore} = useFetch();

    const [scoreType, setScoreType] = useState('');

    const handleSubmit = async () => {
        if (!scoreType.trim()) {
            toast.warn(t('score_type_required'));
            return;
        }

        const result = await createScore('/api/configuration/registers/score/create-score-definitions', {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                score_type: scoreType.trim(),
            }),
        });


        if (result?.score_definition_id) {
            toast.success(t('toast_score_created'));
            setScoreType('');
            onSuccess?.();
            onClose();
        } else {
            toast.error(t('toast_score_create_failed'));
        }
    };

    const handleCancel = () => {
        setScoreType('');
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-neutral-first/80  z-50 flex items-center justify-center p-4">
            <div className="relative w-full max-w-200 max-h-150 bg-primary-first rounded-[10px] overflow-hidden flex p-1">
                <div className="flex-1 w-full bg-neutral-second relative rounded-[10px] overflow-y-hidden p-10">
                    <button
                        onClick={handleCancel}
                        className="absolute top-6 right-6 text-secondary-third hover:text-neutral-first/70 transition-colors"
                    >
                        <X size={40} strokeWidth={2} />
                    </button>

                    <h2 className="text-2xl font-bold text-primary-second mb-4">{t('add_score')}</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-semibold text-neutral-first mb-1">
                                {t('score_type')}
                            </label>
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder={t('enter_score_type')}
                                    value={scoreType}
                                    onChange={(e) => setScoreType(e.target.value)}
                                    className="w-full px-4 py-2 border border-primary-second rounded-lg outline-none outline-1 outline-primary-second transition-all text-neutral-first/70 placeholder:text-secondary-third"
                                />
                            </div>
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
