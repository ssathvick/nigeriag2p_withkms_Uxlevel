"use client";
import { useState, useRef } from "react";
import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";
import { ViewAll } from "@/components/shared";
import { useClickOutside } from "@/shared/hooks/useClickOutside";
import { useNotification } from "@/context/GlobalContext";

export default function NotificationDropdown() {
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const { notifications, unreadCount, isLoading } = useNotification();

    useClickOutside(dropdownRef, () => setOpen(false), open);

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setOpen((prev) => !prev)}
                className="relative p-1"
            >
                <Image
                    src={prefixBasePath("/notification.png")}
                    alt="Notifications"
                    width={24}
                    height={24}
                />
                {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs w-2 h-2 flex items-center justify-center rounded-full">
                        {/* {unreadCount} */}
                    </span>
                )}
            </button>

            {open && (
                <div
                    className="absolute -right-16.5 top-10 mt-3 w-[400px] bg-white border border-gray-200 rounded-[10px] z-50 flex flex-col"
                >
                    <div className="absolute -top-2.5 right-[70px] w-5 h-5 bg-white border-l border-t border-gray-200 rotate-45"></div>

                    <div className="px-6 pb-2 pt-3 text-[18px] font-[500] text-[#ED7C22]">
                        Notifications
                    </div>

                    <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
                        {isLoading && (
                            <>
                                {[1, 2, 3, 4].map((i) => (
                                    <div
                                        key={`loading-${i}`}
                                        className={`pl-4 pr-2 flex items-start ${i % 2 === 0 ? "bg-[#F5F5F5]" : ""}`}
                                    >
                                        <div className="flex gap-3 p-3 w-full animate-pulse">
                                            <div className="flex-shrink-0 w-10 h-10 rounded-md bg-gray-300"></div>

                                            <div className="flex-1 w-full min-w-0">
                                                <div className="h-4 w-32 bg-gray-300 rounded mb-2"></div>
                                                <div className="h-3 w-48 bg-gray-200 rounded mb-1"></div>
                                                <div className="h-3 w-40 bg-gray-200 rounded"></div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </>
                        )}

                        {!isLoading &&
                            notifications.slice(0, 4).map((n, index) => (
                                <div
                                    key={n.id}
                                    className={`pl-4 pr-2 flex items-start ${index % 2 === 0 ? "bg-[#F5F5F5]" : ""}`}
                                >
                                    <div className="flex gap-3 p-3 w-full">
                                        <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-md bg-[#FFF4EB]">
                                            <Image
                                                src={prefixBasePath("/notification_img.png")}
                                                alt="Notification Icon"
                                                width={20}
                                                height={20}
                                            />
                                        </div>

                                        <div className="flex-1 w-full min-w-0">
                                            <h3 className="text-[16px] font-[500] text-black whitespace-normal line-clamp-1">
                                                {n.subject || "Notification"}
                                            </h3>

                                            <p className="text-[14px] font-[400] text-black/60 mt-0.5 line-clamp-1">
                                                {n.body}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))
                        }

                        {!isLoading &&
                            notifications.length > 0 &&
                            notifications.length < 4 &&
                            Array(4 - notifications.length)
                                .fill(null)
                                .map((_, idx) => (
                                    <div
                                        key={`empty-${idx}`}
                                        className={`pl-4 pr-2 flex items-start ${(idx + notifications.length) % 2 === 0 ? "bg-[#F5F5F5]" : ""}`}
                                    >
                                        <div className="flex gap-3 p-3 w-full opacity-40">
                                            <div className="flex-shrink-0 w-10 h-10 rounded-md bg-gray-200"></div>

                                            <div className="flex-1 w-full min-w-0">
                                                <div className="h-4 w-28 bg-transparent rounded mb-2"></div>
                                                <div className="h-3 w-40 bg-transparent rounded mb-1"></div>
                                                <div className="h-3 w-32 bg-transparent rounded"></div>
                                            </div>
                                        </div>
                                    </div>
                                ))
                        }

                        {!isLoading && notifications.length === 0 && (
                            <div className="text-center py-6 text-sm text-gray-500">
                                No notifications yet.
                            </div>
                        )}
                    </div>

                    <div className="border-b-12 border-gray-100"></div>

                    <div className="mt-auto pb-4">
                        <ViewAll
                            href="/notifications"
                            label="View All Notifications"
                            bgColor="#F5F5F5"
                            hoverBgColor="#ED7C22"
                            hoverTextColor="#FFFFFF"
                        />
                    </div>
                </div>
            )}
        </div>
    );
}
