"use client";

import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";

interface AccountRemoveModalProps {
    onClose: () => void;
    onConfirm: () => void;
}

export default function AccountRemoveModal({ onClose, onConfirm }: AccountRemoveModalProps) {
    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl shadow-lg w-[600px] min-h-[300px] p-8 relative flex flex-col items-center justify-center text-center">
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
                    src={prefixBasePath("/remove.png")}
                    alt="Remove"
                    width={80}
                    height={80}
                    className="mb-4"
                />

                <h2 className="text-[#FF3B30] text-[22px] font-[600]">Remove Account</h2>

                <p className="text-gray-700 text-[16px] mt-1 leading-relaxed">
                    You are removing the account. <br />
                    Are you sure?
                </p>

                <div className="mt-6 flex gap-4">
                    <button
                        onClick={onConfirm}
                        className="px-6 py-2 bg-[#FF3B30] text-white rounded-full font-[500]"
                    >
                        Yes
                    </button>
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-gray-100 text-black rounded-full font-[500]"
                    >
                        No
                    </button>
                </div>
            </div>
        </div>
    );
}
