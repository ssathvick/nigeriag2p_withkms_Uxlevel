"use client";

import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";
import { AccountField } from "@/features/accountmapping/components";

interface AccountInfoSectionProps {
    profileImage: string;
    profileName?: string;
    result: any;
}

export default function AccountInfoSection({ profileImage, profileName, result }: AccountInfoSectionProps) {
    const renderAccountFields = () => {
        switch (result.type) {
            case "bank":
                return (
                    <>
                        <AccountField label="Bank Name" value={result.bankName} />
                        <AccountField label="Account Number" value={result.accountNumber} />
                        <AccountField label="Branch Name" value={result.branchName} />
                        <AccountField label="Branch Code" value={result.branchCode} />
                    </>
                );
            case "email":
                return (
                    <>
                        <AccountField label="Email Address" value={result.emailAddress} />
                        <AccountField label="Wallet Provider" value={result.walletProvider} />
                        <AccountField label="Provider Code" value={result.providerCode} />
                    </>
                );
            case "phone":
                return (
                    <>
                        <AccountField label="Mobile Number" value={result.mobileNumber} />
                        <AccountField label="Wallet Provider" value={result.walletProvider} />
                        <AccountField label="Provider Code" value={result.providerCode} />
                    </>
                );
        }
    };

    return (
        <div className="w-[70%] bg-white p-8">
            <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-6">Account Information</h2>

            <div className="flex flex-row gap-10 items-start">
                <Image
                    src={profileImage}
                    alt="Profile"
                    width={40}
                    height={40}
                    className="object-cover rounded-full"
                />

                <div className="flex flex-col justify-start w-full space-y-4">
                    <AccountField label="Name" value={profileName} highlight />
                    {renderAccountFields()}
                </div>
            </div>

            <div className="mt-40 pl-20">
                <label className="block text-[16px] text-black/50 font-[500] mb-1">
                    Powered By
                </label>
                <Image
                    src={prefixBasePath("/spar_acc.png")}
                    alt="SPAR Logo"
                    width={100}
                    height={40}
                    className="object-contain"
                />
            </div>
        </div>
    );
}
