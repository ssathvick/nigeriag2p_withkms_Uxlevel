"use client";

import Image from "next/image";
import { ViewAll } from "@/components/shared";
import { prefixBasePath } from "@/shared/utils/path";

interface Registry {
    name: string;
}

interface RegistryCardProps {
    registries: Registry[];
}

export default function RegistryCard({ registries }: RegistryCardProps) {
    const placeholderRows = Array(Math.max(5 - registries.length, 0)).fill(null);

    return (
        <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] flex-1 mr-[30px] mb-[50px]">
            <div className="flex items-center justify-between h-16 px-8">
                <h3 className="lg:text-[18px]/[21px] xl:text-[18px]/[21px] 2xl:text-[20px]/[23px] font-[600] text-black">
                    My Registries
                </h3>
                <button className="p-1 rounded-full hover:bg-gray-200">
                    <Image
                        src={prefixBasePath("/more.png")}
                        alt="menu"
                        width={18}
                        height={18}
                    />
                </button>
            </div>

            <div className="space-y-0">
                {registries.map((registry, idx) => (
                    <div
                        key={idx}
                        className={`relative ${idx % 2 === 0 ? "bg-[#F5F5F5]" : "bg-white"}`}
                    >
                        <div className="flex items-center justify-start py-4 px-8">
                            <span className="w-2.5 h-2.5 rounded-full bg-gray-400 mr-3 flex-shrink-0"></span>
                            <p className="font-[400] text-black lg:text-[14px] xl:text-[14px] 2xl:text-[16px]">
                                {registry.name}
                            </p>
                        </div>
                    </div>
                ))}

                {placeholderRows.map((_, index) => (
                    <div
                        key={`placeholder-reg-${index}`}
                        className={`${(registries.length + index) % 2 === 0 ? "bg-[#F5F5F5]" : "bg-white"} animate-pulse`}
                    >
                        <div className="flex items-center justify-start py-4 px-8">
                            <div className="w-2.5 h-2.5 rounded-full bg-gray-300 mr-3"></div>
                            <div className="h-5 bg-gray-300 rounded w-3/4"></div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="my-3">
                <ViewAll
                    href="/registries"
                    label="View all Registries"
                    bgColor="#F5F5F5"
                    hoverBgColor="#ED7C22"
                    hoverTextColor="#FFFFFF"
                />
            </div>
        </div>
    );
}
