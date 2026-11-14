'use client';

import { X } from 'lucide-react';
import { useTranslations } from 'next-intl';
import type { ScoreDefinition } from '../shared/types/registers';

interface ViewScoreDefinitionModalProps {
    onClose: () => void;
    data: ScoreDefinition;
}

/** Mount only when open; no `isOpen` prop so the tree is not created until needed. */
export default function ViewScoreDefinitionModal({
    onClose,
    data,
}: ViewScoreDefinitionModalProps) {
    const t = useTranslations();

    return (
        <div className="fixed inset-0 bg-neutral-first/80 z-50 flex items-center justify-center p-4">
            <div className="relative w-full max-w-200 max-h-[95vh] bg-primary-first rounded-[10px] overflow-hidden flex p-1">
                <div className="flex-1 w-full bg-neutral-second relative rounded-[10px] p-10 overflow-y-auto">
                    <button
                        type="button"
                        onClick={onClose}
                        className="absolute top-6 right-6 text-secondary-third hover:text-neutral-first/70 transition-colors focus:outline-none"
                    >
                        <X size={40} strokeWidth={2} />
                    </button>

                    <h2 className="text-2xl font-bold text-primary-second mb-6">
                        {data.score_type} — {t('details')}
                    </h2>

                    <div className="space-y-6">
                        <div className="flex items-start">
                            <div className="w-55 text-[16px] text-secondary-third font-medium shrink-0">
                                {t('score_definition_id')}
                            </div>
                            <div className="flex-1 text-[16px] text-neutral-first font-bold wrap-break-word">
                                {data.score_definition_id || '-'}
                            </div>
                        </div>

                        <div className="flex items-start">
                            <div className="w-55 text-[16px] text-secondary-third font-medium shrink-0">
                                {t('score_type')}
                            </div>
                            <div className="flex-1 text-[16px] text-neutral-first font-bold">
                                {data.score_type || '-'}
                            </div>
                        </div>

                        <div className="flex items-start">
                            <div className="w-55 text-[16px] text-secondary-third font-medium shrink-0">
                                {t('mnemonic')}
                            </div>
                            <div className="flex-1 text-[16px] text-neutral-first font-bold">
                                {data.register_mnemonic || '-'}
                            </div>
                        </div>

                        <div className="flex items-start">
                            <div className="w-55 text-[16px] text-secondary-third font-medium shrink-0">
                                {t('status')}
                            </div>
                            <div className="flex-1 text-[16px] text-neutral-first font-bold">
                                {data.is_enabled ? t('active') : t('inactive')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
