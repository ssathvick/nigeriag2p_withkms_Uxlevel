"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { Profile } from "@/shared/types/profile";

interface ProfileContextType {
    profile: Profile | null;
    setProfile: (value: Profile | null) => void;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export const ProfileContextProvider = ({ children }: { children: ReactNode }) => {
    const [profile, setProfile] = useState<Profile | null>(null);

    useEffect(() => {
        const stored = typeof window !== "undefined" ? localStorage.getItem("profile") : null;
        if (stored) setProfile(JSON.parse(stored));
    }, []);

    useEffect(() => {
        if (typeof window === "undefined") return;

        if (profile === null) localStorage.removeItem("profile");
        else localStorage.setItem("profile", JSON.stringify(profile));
    }, [profile]);

    useEffect(() => {
        const syncLogoutAcrossTabs = () => {
            if (localStorage.getItem("profile") === null) setProfile(null);
        };
        window.addEventListener("storage", syncLogoutAcrossTabs);
        return () => window.removeEventListener("storage", syncLogoutAcrossTabs);
    }, []);

    return (
        <ProfileContext.Provider value={{ profile, setProfile }}>
            {children}
        </ProfileContext.Provider>
    );
};

export const useProfileContext = () => {
    const ctx = useContext(ProfileContext);
    if (!ctx) throw new Error("useProfileContext must be used inside ProfileContextProvider");
    return ctx;
};

export const useAuth = () => {
    const { profile, setProfile } = useProfileContext();
    return { profile, setProfile };
};
