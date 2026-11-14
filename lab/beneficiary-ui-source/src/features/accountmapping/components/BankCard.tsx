import React from 'react';
import Image from "next/image";
import { ViewAll } from '@/components/shared';
import { prefixBasePath } from "@/shared/utils/path";

interface BankCardProps {
    result: any;
    loading: boolean;
}

export default function BankCard({ result, loading }: BankCardProps) {
    const accountData =
        result?.type === "bank"
            ? {
                exists: true,
                type: "bank",
                title: result.bankName,
                value: result.accountNumber,
            }
            : result?.type === "phone"
                ? {
                    exists: true,
                    type: "phone",
                    title: result.walletProvider,
                    value: result.mobileNumber,
                }
                : result?.type === "email"
                    ? {
                        exists: true,
                        type: "email",
                        title: result.walletProvider,
                        value: result.emailAddress,
                    }
                    : {
                        exists: false,
                        type: "unknown",
                    };
    const isLinked = accountData?.exists;

    return (
        <div className="flex flex-col text-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)]">
            <div className="rounded-xl shadow-xl overflow-hidden relative">
                <div className="bg-[#ffcb30] px-8 pt-[30px] pb-[12px] flex justify-between items-end">
                    <div>
                        <h3 className="lg:text-[18px]/[21px] xl:text-[18px]/[21px] 2xl:text-[20px]/[23px] font-[600] text-black">
                            Account/Wallet
                        </h3>
                    </div>

                    <div className="pr-10">
                        <Image
                            src={prefixBasePath("/spar_card.png")}
                            alt="SPAR Card"
                            width={81}
                            height={22}
                            className="object-contain"
                        />
                    </div>
                </div>

                <div className="bg-gradient-to-b from-[#ffbf00] to-[#ED7C22]  pt-[32px] pb-[16px] relative">
                    <div className=" px-[30px] lg:pb-[10px] xl:pb-[10px] 2xl:pb-[8px]">
                        {!loading && isLinked && (
                            <>
                                <div className="lg:text-[14px] xl:text-[14px] 2xl:text-[16px] font-[600] text-black">
                                    {accountData.title}
                                </div>
                                <div className="lg:text-[14px] xl:text-[14px] 2xl:text-[16px] font-[600] text-black">
                                    {accountData.value}
                                </div>
                            </>
                        )}

                        {loading && (
                            <div className="animate-pulse">
                                <div className="lg:h-4 xl:h-4 2xl:h-5 w-2/3 bg-black/30 rounded mb-1"></div>
                                <div className="lg:h-4 xl:h-4 2xl:h-5 w-1/2 bg-black/30 rounded mb-1"></div>
                            </div>
                        )}

                        {!loading && !isLinked && (
                            <>
                                <div className="opacity-0 lg:text-[14px] xl:text-[14px] 2xl:text-[16px] text-black font-[600]">
                                    No linked account found
                                </div>
                                <div className="lg:text-[14px] xl:text-[14px] 2xl:text-[16px] text-black font-[600]">
                                    No linked account found
                                </div>
                            </>
                        )}
                    </div>

                    {loading ? (
                        <div className="mt-3.5 mx-[30px] h-[35px] w-[180px] rounded-[15px] bg-black/20 animate-pulse"></div>
                    ) : (
                        <ViewAll
                            href={isLinked ? "/accounts" : "/accounts/link"}
                            label={isLinked ? "View Account Details" : "Link Account"}
                            bgColor="#FFFFFF66"
                            textColor="#000000"
                            hoverBgColor="#FFFFFF66"
                            hoverTextColor="#ED7C22"
                        />
                    )}

                    <div className="absolute right-12 bottom-0 opacity-20 " >
                        <Image
                            src={prefixBasePath("/account_01.png")}
                            alt="User"
                            width={108}
                            height={102}
                            className="object-contain"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
