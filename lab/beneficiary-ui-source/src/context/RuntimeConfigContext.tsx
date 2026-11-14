"use client";

import { RuntimeConfig } from "@/app/api/_utils/runtimeConfig.server";
import React, { createContext, useContext } from "react";

const RuntimeConfigContext = createContext<RuntimeConfig | null>(null);

export function RuntimeConfigProvider({
    config,
    children,
}: {
    config: RuntimeConfig;
    children: React.ReactNode;
}) {
    return (
        <RuntimeConfigContext.Provider value={config}>
            {children}
        </RuntimeConfigContext.Provider>
    );
}

export function useRuntimeConfig() {
    const ctx = useContext(RuntimeConfigContext);
    if (!ctx) {
        throw new Error("useRuntimeConfig must be used inside RuntimeConfigProvider");
    }
    return ctx;
}
