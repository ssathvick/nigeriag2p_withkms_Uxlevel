import type { Metadata } from "next";
import "@/commons/globals.css";
import 'react-toastify/dist/ReactToastify.css';
import { GlobalContextProvider } from "@/context/GlobalContext";
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getTranslations } from 'next-intl/server';
import { Header } from "@/components/layout";
import { RuntimeConfigProvider } from "@/context/RuntimeConfigContext";
import { RegisterProvider } from "@/context/RegisterContext";
import { ToastContainer } from "react-toastify";
import { Roboto } from 'next/font/google'
import { clientSafeConfig } from '@/app/api/_lib/client-safe-config';
import { getOrigin } from "@/app/api/_lib/get-origin";


const roboto = Roboto({
    weight: ['300', '400', '500', '700'],
    style: ['normal'],
    subsets: ['latin'],
    display: 'swap',
})

export async function generateMetadata({
    params
}: {
    params: Promise<{ locale: string }>;
}): Promise<Metadata> {

    const origin = await getOrigin();

    const { locale } = await params;
    const t = await getTranslations({ locale });
    await clientSafeConfig.fetchRegistryConfig(origin);
    const config = clientSafeConfig.getAll();

    return {
        title: config.registryName || t('registry'),
        description: "",
        icons: {
            icon: config.registryLogo || "/images/common/openg2p_logo.png",
        },
    };
}

export default async function RootLayout({
    children,
    params
}: {
    children: React.ReactNode;
    params: Promise<{ locale: string }>;
}) {

    const origin = await getOrigin();

    const { locale } = await params;
    const messages = await getMessages();

    await clientSafeConfig.fetchRegistryConfig(origin);
    const config = clientSafeConfig.getAll();

    const cssVariables = `
        :root {
            --color-primary-first: ${config.branding?.primary_color_1 ?? "#EABB13"};
            --color-primary-second: ${config.branding?.primary_color_2 ?? "#ED7C22"};
            --color-secondary-first: ${config.branding?.secondary_color_1 ?? "#F3F1F4"};
            --color-secondary-second: ${config.branding?.secondary_color_2 ?? "#E1E1E1"};
            --color-secondary-third: ${config.branding?.secondary_color_3 ?? "#A1A1A1"};
            --color-neutral-first: ${config.branding?.neutral_color_1 ?? "#000000"};
            --color-neutral-second: ${config.branding?.neutral_color_2 ?? "#FFFFFF"};
            --toast-info-color: ${config.branding?.toast_color?.toast_info_color ?? "#007BFF"};
            --toast-success-color: ${config.branding?.toast_color?.toast_success_color ?? "#28A745"};
            --toast-warning-color: ${config.branding?.toast_color?.toast_warning_color ?? "#FFC107"};
            --toast-failed-color: ${config.branding?.toast_color?.toast_failed_color ?? "#DC3545"};
        }
    `;

    return (
        <html lang={locale}>
            <head>
                <style
                    id="branding-css-variables"
                    suppressHydrationWarning
                    dangerouslySetInnerHTML={{ __html: cssVariables }}
                />
            </head>
            <body className={`${roboto.className} antialiased`}>
                <NextIntlClientProvider messages={messages}>
                    <GlobalContextProvider>
                        <RuntimeConfigProvider initialConfig={config}>
                            <Header />
                            <div className="pt-17.5">
                                <RegisterProvider>
                                    <ToastContainer />
                                    {children}
                                </RegisterProvider>
                            </div>
                        </RuntimeConfigProvider>
                    </GlobalContextProvider>
                </NextIntlClientProvider>
            </body>
        </html>
    );
}