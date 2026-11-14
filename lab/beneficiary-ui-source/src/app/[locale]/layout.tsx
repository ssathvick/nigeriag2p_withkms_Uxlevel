import type { Metadata } from "next";
import { ReactNode } from "react";
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { Geist, Geist_Mono } from "next/font/google";

import "@/commons/globals.css";

import { GlobalContextProvider } from "@/context/GlobalContext";

import { prefixBasePath } from '@/shared/utils/path';
import { RuntimeConfigProvider } from "@/context/RuntimeConfigContext";
import { loadRuntimeConfig } from "../api/_utils/runtimeConfig.server";

const geistSans = Geist({
    variable: "--font-geist-sans",
    subsets: ["latin"],
});

const geistMono = Geist_Mono({
    variable: "--font-geist-mono",
    subsets: ["latin"],
});

export const metadata: Metadata = {
    title: "Beneficiary Portal",
    description: "OpenG2P self-service portal for Beneficiaries",
    icons: {
        icon: prefixBasePath("/logo.png"),
    },
};

export const viewport = { width: "device-width", initialScale: 1 };

export async function generateStaticParams() {
    return [{ locale: "en" }, { locale: "de" }];
}

export default async function RootLayout(props: {
    children: ReactNode;
    params: Promise<{ locale: string }>;
}) {
    const { children, params } = props;
    const { locale } = await params;
    const messages = await getMessages({ locale });
    const config = loadRuntimeConfig();

    return (
        <html lang={locale}>
            <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
                <RuntimeConfigProvider config={config}>
                    <NextIntlClientProvider locale={locale} messages={messages}>
                        <GlobalContextProvider>
                            {children}
                        </GlobalContextProvider>
                    </NextIntlClientProvider>
                </RuntimeConfigProvider>
            </body>
        </html>
    );
}
