import { Info } from "./FormInputs";
import type { AccountType } from "@/features/accountmapping/types";

interface InfoSidebarProps {
    accountInfo: any,
}

export function InfoSidebar({ accountInfo }: InfoSidebarProps) {
    return (
        <div className="w-[30%] bg-gray-100 p-8 flex flex-col justify-start gap-4">
            <div className="flex flex-col gap-4">
                <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-2">Information</h2>

                <p className="text-[16px] text-black/70 leading-relaxed">
                    {accountInfo && accountInfo.AccountInfo}
                </p>
            </div>

            {/* <div className="mt-6 flex flex-col items-start gap-3">
                <button
                    disabled
                    className="px-4 py-1 bg-gray-300 text-white font-[500] rounded-full w-auto cursor-not-allowed"
                >
                    Edit Account Information
                </button>
                <button
                    onClick={onRemoveAccount}
                    className="px-4 py-1 bg-[#3399FF] text-white font-[500] rounded-full w-auto"
                >
                    Remove Account
                </button>
            </div> */}
        </div>
    );
}
