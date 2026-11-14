"use client";
import { useState } from "react";
import { useLocale } from "next-intl";
import Image from "next/image";

import { AuthUtil } from '@/features/auth/components';
import { SearchInput } from "@/components/shared";
import { prefixBasePath } from "@/shared/utils/path";
import { useNotification } from "@/context/GlobalContext";


export default function NotificationsPage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const [searchQuery, setSearchQuery] = useState("");

    const { notifications, loadMore, isLoading, markAsRead } = useNotification()

    // const filteredNotifications = notifications.filter(n =>
    //     n.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
    //     n.body.toLowerCase().includes(searchQuery.toLowerCase())
    // );
    const filteredNotifications = notifications

    return (
        <div className="px-[50px] py-4 min-h-screen bg-white">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                Notifications
            </h1>

            <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] overflow-hidden">
                <div className="mb-4 px-6 pt-4 flex items-center justify-between">
                    <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-2">
                        All Notifications
                    </h2>
                    <SearchInput
                        onSearch={(val) => {
                            setSearchQuery(val);
                        }}
                        placeholder="Search"
                        className="w-[200px]"
                    />
                </div>

                <div className="flex flex-col divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
                    {filteredNotifications.map((notification, idx) => (
                        <div
                            key={notification.id}
                            className={`${idx % 2 === 0 ? "bg-gray-100" : "bg-white"} w-full`}
                        >
                            <div className="flex gap-3 px-6 py-3">
                                <div className="bg-white rounded-[16px] flex items-center justify-center flex-shrink-0 w-12 h-12 sm:w-16 sm:h-16">
                                    <Image
                                        src={prefixBasePath("/notification_img.png")}
                                        alt="Notification Icon"
                                        width={40}
                                        height={40}
                                    />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="text-[18px] font-[500] text-black truncate">
                                        {notification.subject}
                                    </h3>
                                    {notification.createdAt && (
                                        <span className="text-[14px] text-[#3399FF] block mt-0.5">
                                            {notification.createdAt}
                                        </span>
                                    )}
                                    <p className="text-xs sm:text-sm text-gray-700 mt-1 line-clamp-2">
                                        {notification.body}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex items-center gap-6 px-8 py-4 text-sm text-black">
                    <button
                        onClick={loadMore}
                        disabled={isLoading}
                        className="px-4 py-2 bg-[#ED7C22] text-white rounded-md hover:bg-[#d56d1f] disabled:opacity-50"
                    >
                        {isLoading ? "Loading..." : "Load More"}
                    </button>
                </div>
            </div>
        </div>
    );
}
