"use client";

import { ReactNode } from "react";
import { ProfileContextProvider, useAuth as useProfileAuth } from "@/context/AuthContext";
import { DepartmentContextProvider, useDepartment as useDeptContext } from "@/context/DepartmentContext";
import { NotificationContextProvider, useNotificationContext } from "@/context/NotificationContext";

export const GlobalContextProvider = ({ children }: { children: ReactNode }) => {
    return (
        <ProfileContextProvider>
            <DepartmentContextProvider>
                <NotificationContextProvider>
                    {children}
                </NotificationContextProvider>
            </DepartmentContextProvider>
        </ProfileContextProvider>
    );
};

export const useAuth = useProfileAuth;
export const useDepartment = useDeptContext;
export const useNotification = useNotificationContext;
