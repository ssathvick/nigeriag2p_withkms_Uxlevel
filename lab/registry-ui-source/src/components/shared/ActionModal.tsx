import { X } from 'lucide-react';
import Image from 'next/image';
import { useTranslations } from 'next-intl';

interface ActionModalProps {
    isOpen: boolean;
    type: 'warning' | 'success' | 'error';
    title: string;
    subtitle: string;
    onClose: () => void;
    onConfirm?: () => void;
    confirmText?: string;
    cancelText?: string;
    hideCancel?: boolean;
}

export default function ActionModal({
    isOpen,
    type,
    title,
    subtitle,
    onClose,
    onConfirm,
    confirmText,
    cancelText,
    hideCancel = false,
}: ActionModalProps) {
    const t = useTranslations();
    const finalConfirmText = confirmText || t('save');
    const finalCancelText = cancelText || t('cancel');

    if (!isOpen) return null;

    const borderColor = type === 'warning' ? 'border-primary-first' : type === 'error' ? 'border-toast-failed' : 'border-toast-success';

    return (
        <div className="fixed inset-0 bg-neutral-first/50 z-[100] flex items-center justify-center p-4">
            <div className={`relative w-full max-w-[450px] bg-neutral-second rounded-[20px] shadow-lg flex flex-col items-center p-8 border-4 ${borderColor}`}>
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-secondary-third hover:text-neutral-first/70 transition-colors"
                >
                    <X size={24} strokeWidth={2} />
                </button>

                <div className="mb-6 mt-4">
                    {type === 'warning' ? (
                        <div className="w-20 h-20 bg-secondary-first rounded-full flex items-center justify-center">
                            <div className="w-14 h-14 bg-toast-warning rounded-full flex items-center justify-center">
                                <span className="text-neutral-second text-[32px] font-bold">!</span>
                            </div>
                        </div>
                    ) : type === 'error' ? (
                        <div className="w-20 h-20 relative rounded-full flex items-center justify-center border-10 border-toast-failed/10 bg-toast-failed/80">
                            <Image
                                src="/images/common/wrongsymbol.png"
                                alt={t('error')}
                                width={41}
                                height={30}
                                className="object-contain"
                            />
                        </div>
                    ) : (
                        <div className="w-20 h-20 relative rounded-full flex items-center justify-center border-10 border-toast-success/10 bg-toast-success/80">
                            <Image
                                src="/images/common/rightsymbol.png"
                                alt={t('success')}
                                width={41}
                                height={30}
                                className="object-contain"
                            />
                        </div>
                    )}
                </div>

                <h2 className="text-[22px] font-bold text-neutral-first mb-2 text-center">{title}</h2>
                <p className="text-secondary-third text-[14px] text-center mb-8 px-4">
                    {subtitle}
                </p>

                <div className="flex gap-4 w-full justify-center">
                    {!hideCancel && (
                        <button
                            onClick={onClose}
                            className="px-8 py-2.5 bg-secondary-second text-neutral-first font-semibold rounded-full hover:bg-secondary-third transition-colors text-[14px]"
                        >
                            {finalCancelText}
                        </button>
                    )}
                    {onConfirm && (
                        <button
                            onClick={onConfirm}
                            className="px-8 py-2.5 bg-neutral-first text-neutral-second font-semibold rounded-full hover:bg-secondary-second-800 transition-colors text-[14px]"
                        >
                            {finalConfirmText}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
