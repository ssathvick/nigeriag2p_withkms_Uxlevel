"use client";

import Image from "next/image";
import { useTranslations } from "next-intl";

interface Props {
    onConfirm: () => void;
    onClose: () => void;
    loading?: boolean;
    messageKey: string;
}

export default function ConfirmRemovePopup({
    onConfirm,
    onClose,
    loading,
    messageKey
}: Props) {
    const t = useTranslations();

    return (
        <div className="fixed inset-0 bg-neutral-first/80 flex items-center justify-center z-50">
            <div className="relative bg-neutral-second rounded-[10px] border-5 border-toast-failed w-120 p-6 flex flex-col items-center gap-6">
                <button
                    className="absolute top-4 right-4 opacity-50"
                    onClick={onClose}
                >
                    <Image
                        src="/images/changerequest/cr_close.png"
                        alt="Close"
                        width={20}
                        height={20}
                    />
                </button>

                <div className="w-16 h-16 rounded-full border-8 border-toast-failed/10 bg-toast-failed/80 flex items-center justify-center">
                    <Image
                        src="/images/changerequest/cr_reject.png"
                        alt="Warning"
                        width={30}
                        height={24}
                    />
                </div>

                <h3 className="text-[20px] font-semibold text-center">
                    {t("are_you_sure")}
                </h3>

                <p className="text-[16px] text-center text-neutral-first/70">
                    {t(messageKey)}
                </p>

                <div className="flex gap-4 mt-2">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 rounded-[10px] bg-[black] text-neutral-second"
                    >
                        {t("cancel")}
                    </button>

                    <button
                        onClick={onConfirm}
                        disabled={loading}
                        className="px-6 py-2 rounded-[10px] bg-toast-failed text-neutral-second"
                    >
                        {t("remove")}
                    </button>
                </div>
            </div>
        </div>
    );
}