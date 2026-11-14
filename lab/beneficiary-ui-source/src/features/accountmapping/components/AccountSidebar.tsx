"use client";

interface AccountSidebarProps {
    accountInfo: any,
    result: any;
    unlinking: boolean;
    onEdit: () => void;
    onRemove: () => void;
}

export default function AccountSidebar({ accountInfo, result, unlinking, onEdit, onRemove }: AccountSidebarProps) {
    return (
        <div className="w-[30%] bg-gray-100 p-8 flex flex-col justify-between gap-4">
            <div className="flex flex-col gap-4">
                <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-2">Information</h2>

                <p className="text-[16px] text-black/70 leading-relaxed">
                    {accountInfo && accountInfo.AccountInfo}
                </p>
            </div>

            <div className="flex-1"></div>

            <div className="flex-1"></div>

            <div className="flex flex-col items-start gap-3 mt-6">
                <button
                    onClick={onEdit}
                    className="px-4 py-1 bg-[#3399FF] text-white font-[500] rounded-full w-auto"
                >
                    Edit Account Information
                </button>

                <button
                    disabled={unlinking}
                    onClick={onRemove}
                    className="px-4 py-1 bg-[#3399FF] text-white font-[500] rounded-full w-auto"
                >
                    {unlinking ? "Removing..." : "Remove Account"}
                </button>
            </div>
        </div>
    );
}
