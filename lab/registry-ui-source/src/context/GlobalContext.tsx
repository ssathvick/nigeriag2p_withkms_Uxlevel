"use client";

import { ReactNode } from "react";
import { NotificationContextProvider, useNotificationContext } from "@/context/NotificationContext";
import { AuthProvider } from "@/context/Authcontext";
import { RbacProvider } from "@/context/RbacContext";

export const GlobalContextProvider = ({ children }: { children: ReactNode }) => {
    return (
        <AuthProvider>
            <RbacProvider>
                <NotificationContextProvider>
                    {children}
                </NotificationContextProvider>
            </RbacProvider>
        </AuthProvider>
    );
};

export const useNotification = useNotificationContext;
