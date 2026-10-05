'use client';

import { X } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface BaseModalProps {
    title: string;
    onClose: () => void;
    children: React.ReactNode;
    primaryActionLabel?: string;
    onPrimaryAction?: () => void;
    maxWidth?: string;
    hideCancel?: boolean;
    secondaryActionLabel?: string;
}

export default function BaseModal({
    title,
    onClose,
    children,
    primaryActionLabel,
    onPrimaryAction,
    maxWidth = 'max-w-150',
    hideCancel = false,
    secondaryActionLabel,
}: BaseModalProps) {
    const t = useTranslations();
    return (
        <div className="fixed inset-0 bg-neutral-first/80 z-50 flex items-center justify-center">
            <div className={`relative w-full ${maxWidth} bg-neutral-second rounded-[10px] border-5 border-primary-first px-8 py-6`}>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-[24px] text-primary-second font-medium">
                        {title}
                    </h2>

                    <button
                        onClick={onClose}
                        className="opacity-50 hover:opacity-100 transition"
                    >
                        <X size={30} />
                    </button>
                </div>

                <div className="space-y-4 max-h-[70vh] overflow-y-auto modal-scroll">
                    {children}
                    <div className="flex gap-4 pt-2">
                        {!hideCancel && (
                            <button
                                onClick={onClose}
                                className="px-6 py-2 bg-secondary-second text-neutral-first/50 text-[16px] font-bold rounded-[10px]"
                            >
                                {secondaryActionLabel || t('cancel')}
                            </button>
                        )}

                        {primaryActionLabel && onPrimaryAction && (
                            <button
                                onClick={onPrimaryAction}
                                className="px-6 py-2 bg-neutral-first text-neutral-second text-[16px] font-bold rounded-[10px]"
                            >
                                {primaryActionLabel}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}