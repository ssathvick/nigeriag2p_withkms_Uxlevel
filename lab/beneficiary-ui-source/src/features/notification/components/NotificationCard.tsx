"use client";

import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";
import { ViewAll } from "@/components/shared";

interface Notification {
    id: string;
    title: string;
    description: string;
}

interface NotificationCardProps {
    notifications: Notification[];
}

export default function NotificationCard({ notifications }: NotificationCardProps) {
    return (
        <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] flex-1 mb-[50px] mr-[50px]">
            <div className="flex items-center justify-between h-16 px-8">
                <h3 className="text-[18px] hd1366:text-[19px] hd1536:text-[20px] font-[600] text-black">
                    Latest News
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

            <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
                {notifications.map((n, idx) => (
                    <div key={n.id} className={`${idx % 2 === 0 ? "bg-[#F5F5F5]" : ""}`}>
                        <div className="flex gap-4 px-8 py-3">
                            <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-md bg-[#FFF4EB]">
                                <Image
                                    src={prefixBasePath("/notification_img.png")}
                                    alt="Notification Icon"
                                    width={20}
                                    height={20}
                                />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-[14px] hd1366:text-[15px] hd1536:text-[16px] font-[600] text-black">
                                    {n.title}
                                </h3>
                                <p className="text-[13px] hd1366:text-[14px] hd1536:text-[15px] font-[400] text-black/50 mt-0.5 line-clamp-2">
                                    {n.description}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="my-3">
                <ViewAll
                    href="/news"
                    label="View latest News"
                    bgColor="#F5F5F5"
                    hoverBgColor="#ED7C22"
                    hoverTextColor="#FFFFFF"
                />
            </div>
        </div>
    );
}
