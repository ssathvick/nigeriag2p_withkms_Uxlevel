"use client";

import { createContext, useContext, ReactNode } from "react";
import { useNovuNotifications } from "@/features/notification/utils/useNovuNotifications";

interface NotificationContextType {
    notifications: any[];
    unreadCount: number;
    loadMore: () => void;
    isLoading: boolean;
    markAsRead: (notificationId: string) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationContextProvider = ({ children }: { children: ReactNode }) => {
    // here, the profile auth has removed 
    const subscriberId = "123"
    const applicationIdentifier = process.env.NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER ?? "";

    const { notifications, unreadCount, loadMore, isLoading, markAsRead } = useNovuNotifications(
        subscriberId,
        applicationIdentifier,
        5
    );

    return (
        <NotificationContext.Provider
            value={{
                notifications,
                unreadCount,
                loadMore,
                isLoading,
                markAsRead,
            }}
        >
            {children}
        </NotificationContext.Provider>
    );
};

export const useNotificationContext = () => {
    const ctx = useContext(NotificationContext);
    if (!ctx) throw new Error("useNotificationContext must be used inside NotificationContextProvider");
    return ctx;
};

export const useNotification = () => {
    const { notifications, unreadCount, loadMore, isLoading } = useNotificationContext();
    return { notifications, unreadCount, loadMore, isLoading };
};
