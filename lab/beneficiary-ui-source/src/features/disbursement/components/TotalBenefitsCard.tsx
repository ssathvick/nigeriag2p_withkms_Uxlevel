import React from 'react';
import Image from "next/image";

import { ViewAll } from '@/components/shared';
import { prefixBasePath } from "@/shared/utils/path";
import { BenefitCardData } from "@/features/disbursement/types";

interface TotalBenefitsCardProps {
    benefits: BenefitCardData[];
    loading: boolean;
}

export default function TotalBenefitsCard({ benefits, loading }: TotalBenefitsCardProps) {
    return (
        <div className="flex flex-col text-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)]">
            <div className="rounded-xl shadow-xl overflow-hidden relative">
                <div className="bg-[#ffcb30] px-8 pt-[30px] pb-[12px] flex justify-between items-end">
                    <h3 className="lg:text-[18px]/[21px] xl:text-[18px]/[21px] 2xl:text-[20px]/[23px] font-[600] text-black">
                        Benefits Received till date
                    </h3>
                </div>

                <div className="relative bg-gradient-to-b from-[#ffbf00] to-[#ED7C22] pt-4  pb-[18px] overflow-hidden">
                    <div className="absolute right-16 bottom-0 opacity-20 pointer-events-none select-none z-0">
                        <Image
                            src={prefixBasePath("/dollar.png")}
                            alt="Dollar Icon"
                            width={68}
                            height={104}
                            className="object-contain"
                        />
                    </div>

                    <div className="flex justify-between items-center w-full px-6">
                        {!loading && benefits.map((b, index) => (
                            <div
                                key={index}
                                className=" flex flex-col items-center text-center min-w-[70px] z-10"
                            >
                                <div className="mb-1 w-[34px] h-[34px] rounded-full bg-[#FFFFFF80] flex items-center justify-center">
                                    <Image
                                        src={prefixBasePath(b.icon)}
                                        alt={b.label}
                                        width={25}
                                        height={25}
                                        className="object-contain"
                                    />
                                </div>

                                <div className="lg:text-[18px] xl:text-[18px] 2xl:text-[20px] text-white font-[700]">{b.value}</div>
                                <div className="lg:text-[14px] xl:text-[14px] 2xl:text-[16px] text-black font-[600]">{b.label}</div>
                            </div>
                        ))}
                        {loading &&
                            Array(4)
                                .fill(0)
                                .map((_, index) => (
                                    <div
                                        key={`placeholder-${index}`}
                                        className="flex flex-col items-center text-center min-w-[70px] animate-pulse"
                                    >
                                        <div className="h-[34px] w-[34px] rounded-full bg-white/50 mb-1" />
                                        <div className="lg:h-5 xl:h-5 2xl:h-6 w-10 bg-white/40 rounded-[15px] mb-1" />
                                        <div className="lg:h-5 xl:h-5 2xl:h-6 w-12 bg-black/20 rounded-[15px]" />
                                    </div>
                                ))}
                    </div>

                    {loading ? (
                        <div className="mt-4 mx-[30px] h-[35px] w-[180px] rounded-[15px] bg-black/20 animate-pulse"></div>
                    ) : (
                        <ViewAll
                            href="/benefits"
                            label="View All Benefits"
                            bgColor="#FFFFFF66"
                            textColor="#000000"
                            hoverBgColor="#FFFFFF66"
                            hoverTextColor="#ED7C22"
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
