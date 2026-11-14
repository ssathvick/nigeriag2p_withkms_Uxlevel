"use client";

import { useEffect, useState, useRef } from "react";
import { Novu } from "@novu/js";
import { Notification } from "@/features/notification/types";

// const backendUrl = process.env.NOVU_BACKEND_URL;
// const socketUrl = process.env.NOVU_SOCKET_URL;

export function useNovuNotifications(
    subscriberId: string,
    applicationIdentifier: string,
    limit: number = 5
) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [offset, setOffset] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    const novuRef = useRef<Novu | null>(null);

    // const initNovu = () => {
    //     if (!novuRef.current) {
    //         novuRef.current = new Novu({ subscriberId, applicationIdentifier, backendUrl, socketUrl });
    //     }
    //     return novuRef.current;
    // };

    const initNovu = () => {
        if (!novuRef.current) {
            novuRef.current = new Novu({ subscriberId, applicationIdentifier });
        }
        return novuRef.current;
    };

    const formatNotification = (n: any): Notification => ({
        id: n.id,
        subject: n.subject,
        body: n.body,
        createdAt: n.createdAt,
        isRead: n.isRead,
        isSeen: n.isSeen,
        isArchived: n.isArchived,
        avatar: n.avatar,
    });

    const fetchUnreadCount = async () => {
        if (!subscriberId || !applicationIdentifier) return;
        try {
            const novu = initNovu();
            const countResponse = await novu.notifications.count({ read: false });
            setUnreadCount(countResponse?.data?.count ?? 0);
        } catch (error) {
            console.error("Error fetching unread count:", error);
        }
    };

    const loadMore = async () => {
        if (isLoading || !subscriberId || !applicationIdentifier) return;

        setIsLoading(true);
        const novu = initNovu();

        try {
            const listResponse = await novu.notifications.list({ limit: limit, offset });
            const raw = listResponse?.data?.notifications ?? [];

            const formatted = raw.map(formatNotification);

            setNotifications(prev => {
                const existingIds = new Set(prev.map(n => n.id));
                const newItems = formatted.filter(n => !existingIds.has(n.id));
                return [...prev, ...newItems];
            });

            setOffset(prev => prev + limit);
        } catch (error) {
            console.error("Error fetching notifications:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const markAsRead = async (notificationId: string) => {
        const novu = initNovu();
        try {
            await novu.notifications.read({ notificationId });

            setNotifications(prev =>
                prev.map(n => n.id === notificationId ? { ...n, isRead: true } : n)
            );

            setUnreadCount(prev => Math.max(prev - 1, 0));
        } catch (error) {
            console.error("Error marking as read:", error);
        }
    };

    useEffect(() => {
        if (!subscriberId || !applicationIdentifier) return;

        const novu = initNovu();

        const handleNewNotification = (event: any) => {
            const n = event?.result;
            if (!n) return;

            const newNotification = formatNotification(n);

            setNotifications(prev => {
                if (prev.some(x => x.id === newNotification.id)) return prev;
                return [newNotification, ...prev];
            });

            setOffset(prev => prev + 1);
            setUnreadCount(prev => prev + 1);
        };

        const unsubscribeReceived = novu.on(
            "notifications.notification_received",
            handleNewNotification
        );

        return () => unsubscribeReceived();
    }, [subscriberId, applicationIdentifier]);

    useEffect(() => {
        setNotifications([]);
        setOffset(0);
        loadMore();
        fetchUnreadCount();
    }, [subscriberId, applicationIdentifier]);

    return { notifications, unreadCount, loadMore, isLoading, markAsRead };
}
