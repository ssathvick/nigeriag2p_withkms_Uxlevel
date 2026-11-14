"use client";

import { useState } from "react";
import Image from "next/image";
import { useTranslations } from "next-intl";

interface Props {
    onSubmit: (reason: string) => void;
    onClose: () => void;
    loading?: boolean;
}

export default function RejectReasonPopup({
    onSubmit,
    onClose,
    loading,
}: Props) {
    const [reason, setReason] = useState("");
    const t = useTranslations();

    return (
        <div className="fixed inset-0 bg-neutral-first/80 flex items-center justify-center z-50">
            <div className="relative bg-neutral-second rounded-[10px] border-10 border-toast-failed/80 w-150 h-100 p-6 flex flex-col items-center justify-center gap-4">
                <button
                    className="absolute top-10 right-10 opacity-50"
                    onClick={onClose}
                >
                    <Image src="/images/changerequest/cr_close.png" alt="Close" width={30} height={30} />
                </button>

                <div className="w-20 h-20 rounded-full border-10 border-toast-failed/10 bg-toast-failed/80 flex items-center justify-center">
                    <Image
                        src="/images/changerequest/cr_reject.png"
                        alt="Reject"
                        width={41}
                        height={30}
                    />
                </div>

                <h3 className="text-[24px] font-semibold text-centser">
                    {t("reject_title")}
                </h3>

                <div className="w-full max-w-105 mt-2">
                    <p className="text-[16px] text-neutral-first mb-1">
                        {t("reject_description")}

                    </p>

                    <div className="flex gap-2">
                        <input
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                            placeholder={t("reject_placeholder")}
                            className="flex-1 border-2 border-black/20 rounded-[10px] px-4 py-2 focus:outline-none"
                        />
                        <button
                            disabled={!reason || loading}
                            onClick={() => onSubmit(reason)}
                            className="bg-neutral-first text-neutral-second px-8 rounded-[10px]"
                        >
                            {t("submit")}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
