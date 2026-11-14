"use client";

import { useRouter } from "next/navigation";

export default function AccountEmptyState({ lang }: { lang: string }) {
    const router = useRouter();

    return (
        <div className="relative px-[50px] py-4 bg-white min-h-screen">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                Account / Wallet
            </h1>

            <div className="flex justify-center items-center">
                <div className="w-full min-h-[75vh] flex flex-col justify-center items-center text-center bg-white p-8 rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)]">
                    <h2 className="text-[22px] font-[600] text-gray-800 mb-4">
                        No Linked Account Found
                    </h2>

                    <p className="text-[16px] text-gray-600 mb-6">
                        You currently don't have any linked account or wallet.
                        Please link an account to proceed.
                    </p>

                    <button
                        onClick={() => router.push(`/${lang}/accounts/link`)}
                        className="px-6 py-2 bg-black text-white font-[500] rounded-full transition-all"
                    >
                        Link Account
                    </button>
                </div>
            </div>
        </div>
    );
}
