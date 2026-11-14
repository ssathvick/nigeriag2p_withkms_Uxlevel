"use client";

import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";

interface AccountSuccessModalProps {
    onClose: () => void;
    onBack?: () => void;
}

export default function AccountSuccessModal({ onClose, onBack }: AccountSuccessModalProps) {
    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-lg w-[600px] min-h-[450px] p-8 relative flex flex-col items-center justify-center text-center">
                <div className="absolute top-6 right-6">
                    <button onClick={onClose} className="hover:opacity-70 transition">
                        <Image
                            src={prefixBasePath("/close.png")}
                            alt="Close"
                            width={20}
                            height={20}
                            className="opacity-50"
                            priority
                        />
                    </button>
                </div>

                <Image
                    src={prefixBasePath("/successful.png")}
                    alt="Success"
                    width={80}
                    height={80}
                    className="mb-4"
                />

                <h2 className="text-[#00B765] text-[22px] font-[600]">Thank You</h2>
                <p className="text-gray-700 text-[16px] mt-1">
                    Your account information <br />
                    updated successfully.
                </p>

                <button
                    onClick={onBack || (() => window.history.back())}
                    className="mt-6 px-6 py-2 bg-black text-white rounded-full font-[500]"
                >
                    Back
                </button>
            </div>
        </div>
    );
}
