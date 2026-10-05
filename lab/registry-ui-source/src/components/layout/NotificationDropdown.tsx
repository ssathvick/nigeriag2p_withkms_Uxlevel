"use client";
import { useState, useRef } from "react";
import Image from "next/image";
import { ViewAll } from "@/components/shared";
import { useClickOutside } from "@/shared/hooks/useClickOutside";
import { useNotification } from "@/context/GlobalContext";
import { useTranslations } from 'next-intl';

export default function NotificationDropdown() {
    const [open, setOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const t = useTranslations();

    const { notifications, unreadCount, isLoading } = useNotification();

    useClickOutside(dropdownRef, () => setOpen(false), open);

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setOpen((prev) => !prev)}
                className="relative p-1"
            >
                <Image
                    src="/images/messages/notification.png"
                    alt={t('notifications')}
                    width={24}
                    height={24}
                />
                {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-neutral-second text-xs w-2 h-2 flex items-center justify-center rounded-full">
                        {/* {unreadCount} */}
                    </span>
                )}
            </button>

            {open && (
                <div
                    className="absolute -right-16.5 top-10 mt-3 w-100 bg-neutral-second border border-gray-200 rounded-[10px] z-50 flex flex-col"
                >
                    <div className="absolute -top-2.5 right-17.5 w-5 h-5 bg-neutral-second border-l border-t border-gray-200 rotate-45"></div>

                    <div className="px-6 pb-2 pt-3 text-[18px] font-medium text-primary-second">
                        {t('notifications')}
                    </div>

                    <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
                        {isLoading && (
                            <>
                                {[1, 2, 3, 4].map((i) => (
                                    <div
                                        key={`loading-${i}`}
                                        className={`pl-4 pr-2 flex items-start ${i % 2 === 0 ? "bg-secondary-first" : ""}`}
                                    >
                                        <div className="flex gap-3 p-3 w-full animate-pulse">
                                            <div className="shrink-0 w-10 h-10 rounded-md bg-secondary-third"></div>

                                            <div className="flex-1 w-full min-w-0">
                                                <div className="h-4 w-32 bg-secondary-third rounded mb-2"></div>
                                                <div className="h-3 w-48 bg-secondary-second rounded mb-1"></div>
                                                <div className="h-3 w-40 bg-secondary-second rounded"></div>
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
                                    className={`pl-4 pr-2 flex items-start ${index % 2 === 0 ? "bg-secondary-first" : ""}`}
                                >
                                    <div className="flex gap-3 p-3 w-full">
                                        <div className="shrink-0 w-10 h-10 flex items-center justify-center rounded-md bg-secondary-first">
                                            <Image
                                                src="/images/messages/notification_img.png"
                                                alt={t('notification')}
                                                width={20}
                                                height={20}
                                            />
                                        </div>

                                        <div className="flex-1 w-full min-w-0">
                                            <h3 className="text-[16px] font-medium text-neutral-first whitespace-normal line-clamp-1">
                                                {n.subject || t('notification')}
                                            </h3>

                                            <p className="text-[14px] font-normal text-neutral-first/60 mt-0.5 line-clamp-1">
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
                                        className={`pl-4 pr-2 flex items-start ${(idx + notifications.length) % 2 === 0 ? "bg-secondary-first" : ""}`}
                                    >
                                        <div className="flex gap-3 p-3 w-full opacity-40">
                                            <div className="shrink-0 w-10 h-10 rounded-md bg-secondary-second"></div>

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
                            <div className="text-center py-6 text-sm text-neutral-first/50">
                                {t('no_notifications')}
                            </div>
                        )}
                    </div>

                    <div className="border-b-12 border-secondary-first"></div>

                    <div className="mt-auto pb-4 ml-6">
                        <ViewAll
                            href="/notifications"
                            label={t('view_all_notifications')}
                            bgColor="var(--color-secondary-first)"
                            hoverBgColor="var(--color-primary-second)"
                            hoverTextColor="var(--color-neutral-second)"
                        />
                    </div>
                </div>
            )}
        </div>
    );
}
