"use client";

import { createContext, useContext, ReactNode } from "react";
import {useAuth} from '@/context/Authcontext';
import { useNovuNotifications } from "@/features/notification/utils/useNovuNotifications";

interface NotificationContextType {
    isAvailable: boolean;
    notifications: any[];
    unreadCount: number;
    loadMore: () => void;
    isLoading: boolean;
    markAsRead: (notificationId: string) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationContextProvider = ({ children }: { children: ReactNode }) => {
    // Never subscribe different registry users through a shared placeholder identity.
    const {user}=useAuth();
    const subscriberId = String(user?.notification_subscriber_id||user?.sub||'');
    const applicationIdentifier = process.env.NEXT_PUBLIC_NOVU_APPLICATION_IDENTIFIER ?? "";

    const isAvailable=Boolean(subscriberId&&applicationIdentifier);
    const { notifications, unreadCount, loadMore, isLoading, markAsRead } = useNovuNotifications(
        subscriberId,
        applicationIdentifier,
        5
    );

    return (
        <NotificationContext.Provider
            value={{
                isAvailable,
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
