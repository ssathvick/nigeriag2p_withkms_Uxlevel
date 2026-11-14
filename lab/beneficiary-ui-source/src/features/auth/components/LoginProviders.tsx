"use client";
import { useState, useEffect } from "react";
import { useLocale } from "next-intl";

import { prefixBaseApiPath, prefixBasePath } from '@/shared/utils/path';
import { LoginProvider } from "@/features/auth/types/loginprovider";

export default function LoginProviders() {
    const locale = useLocale();
    const [loginProviders, setLoginProviders] = useState<LoginProvider[]>([]);

    useEffect(() => {
        fetch(prefixBaseApiPath(`/auth/get_login_providers`))
            .then((res) => res.json())
            .then((resJson: { loginProviders: LoginProvider[] }) => {
                const providers = resJson.loginProviders.map((x) => {
                    if (typeof x.displayName !== "string") {
                        const displayNameLocale = Object.keys(x.displayName)[0];
                        x.displayName = x.displayName[displayNameLocale] || "";
                    }
                    return x;
                });
                setLoginProviders(providers);
            })
            .catch((err) => console.error("Failed to fetch login providers:", err));
    }, []);

    return (
        <div className="mt-1 w-full">
            {loginProviders.map((x) => (
                <div key={x.id} className="mb-2">
                    <a
                        href={prefixBaseApiPath(
                            `/auth/get_login_provider_redirect/${x.id}?redirect_uri=${encodeURIComponent(window.location.origin + prefixBasePath(`/${locale}/dashboard`))}`
                        )}
                        className="block w-full py-2 rounded-[20px] text-[16px] bg-black text-white font-semibold text-center hover:text-[#ED7C22] hover:bg-black/90 transition"
                    >
                        {x.displayName}
                    </a>
                </div>
            ))}
        </div>
    );
}
