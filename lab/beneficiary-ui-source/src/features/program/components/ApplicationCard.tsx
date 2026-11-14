"use client";

import Image from "next/image";
import { ViewAll } from "@/components/shared";
import { prefixBasePath } from "@/shared/utils/path";

interface Application {
    name: string;
    status: string;
}

interface ApplicationCardProps {
    applications: Application[];
}

const getStatusClasses = (status: string) => {
    let bgClass = "";
    let textClass = "";

    switch (status.toLowerCase()) {
        case "applied":
            bgClass = "bg-[rgba(51,153,255,0.2)]";
            textClass = "text-[#3399FF]";
            break;
        case "progress":
            bgClass = "bg-[rgba(0,183,101,0.2)]";
            textClass = "text-[#00B765]";
            break;
        case "pending":
            bgClass = "bg-[rgba(237,124,34,0.2)]";
            textClass = "text-[#ED7C22]";
            break;
        default:
            bgClass = "bg-gray-200";
            textClass = "text-gray-600";
            break;
    }

    return { bgClass, textClass };
};

export default function ApplicationCard({ applications }: ApplicationCardProps) {
    const placeholderRows = Array(Math.max(4 - applications.length, 0)).fill(null);

    return (
        <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] flex-1 mr-[50px] mb-[50px]">
            <div className="flex items-center justify-between h-16 px-8">
                <h3 className="lg:text-[18px]/[21px] xl:text-[18px]/[21px] 2xl:text-[20px]/[23px] font-[600] text-black">
                    My Applications
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

            <div className="flex px-8 py-4 bg-[#F5F5F5] font-[700] text-black lg:text-[15px] xl:text-[15px] 2xl:text-[17px]">
                <span className="flex-1">Name</span>
                <span className="min-w-[90px]">Status</span>
            </div>

            <div className="space-y-0">
                {applications.map((app, idx) => {
                    const { bgClass, textClass } = getStatusClasses(app.status);
                    return (
                        <div
                            key={idx}
                            className={`relative ${idx % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]"}`}
                        >
                            <div className="flex items-center justify-start py-3 px-8">
                                <p className="flex-1 truncate font-[400] text-black lg:text-[14px] xl:text-[14px] 2xl:text-[16px]">
                                    {app.name}
                                </p>
                                <p
                                    className={`min-w-[90px] text-center font-[400] rounded-full px-1 py-1 lg:text-[14px] xl:text-[14px] 2xl:text-[16px] ${bgClass} ${textClass}`}
                                >
                                    {app.status}
                                </p>
                            </div>
                        </div>
                    );
                })}
                {placeholderRows.map((_, index) => (
                    <div
                        key={`placeholder-${index}`}
                        className={`${(applications.length + index) % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]"} animate-pulse`}
                    >
                        <div className="flex items-center justify-start py-4 px-8">
                            <div className="flex-1">
                                <div className="h-5 bg-gray-300 rounded w-3/4"></div>
                            </div>

                            <div className="min-w-[90px]">
                                <div className="h-5 bg-gray-300 rounded-full w-full"></div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="my-3">
                <ViewAll
                    href="/applications"
                    label="View all Applications"
                    bgColor="#F5F5F5"
                    hoverBgColor="#ED7C22"
                    hoverTextColor="#FFFFFF"
                />
            </div>
        </div>
    );
}
