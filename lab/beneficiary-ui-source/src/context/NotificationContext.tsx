"use client";

import { createContext, useContext, ReactNode } from "react";
import { useNovuNotifications } from "@/features/notification/utils/useNovuNotifications";
import { useAuth } from "@/context/GlobalContext";
import { useRuntimeConfig } from "./RuntimeConfigContext";

interface NotificationContextType {
    notifications: any[];
    unreadCount: number;
    loadMore: () => void;
    isLoading: boolean;
    markAsRead: (notificationId: string) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationContextProvider = ({ children }: { children: ReactNode }) => {
    const { profile } = useAuth();
    const subscriberId = profile?.provider_unique_id ?? "";
    const { novu } = useRuntimeConfig();
    const applicationIdentifier = novu.applicationIdentifier;

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
