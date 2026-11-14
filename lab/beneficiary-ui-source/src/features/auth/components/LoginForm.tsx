"use client";

import Image from "next/image";
import { SyntheticEvent } from "react";
import { useTranslations } from "next-intl";

import LoginProviders from '@/features/auth/components/LoginProviders';

import { prefixBasePath } from '@/shared/utils/path';

export default function LoginForm() {
    const t = useTranslations("loginPage");

    function handleSubmit(e: SyntheticEvent) {
        e.preventDefault();
        console.log("Login submitted");
    }

    return (
        <div className="w-[420px] h-[540px] bg-[linear-gradient(180deg,#FEF1C1_0%,#FCBE00_100%)] rounded-[20px] shadow-[0_4px_20px_0_rgba(0,0,0,0.25)] flex flex-col items-center p-6">
            <Image
                src={prefixBasePath("/openg2p_logo.png")}
                alt={t("portalName")}
                width={80}
                height={80}
                priority
                className="mb-4"
            />

            <p className="text-[30px] font-medium text-black mb-6">{t("portalName")}</p>

            <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4 px-8">
                <div className="flex flex-col">
                    <label className="mb-1 text-[16px] font-medium text-black">
                        {t("emailOrPhone")}
                    </label>
                    <input
                        type="text"
                        placeholder="Enter your email"
                        className="px-4 py-2 text-black bg-white rounded-[10px] placeholder-[#00000040] focus:outline-none"
                    />
                </div>

                <div className="flex flex-col">
                    <label className="mb-1 text-[16px] font-medium text-black">{t("password")}</label>
                    <input
                        type="password"
                        placeholder="Enter your password"
                        className="px-4 py-2 text-black bg-white rounded-[10px] placeholder-[#00000040] focus:outline-none"
                    />
                    <div className="flex justify-end mt-1">
                        <a
                            href="/reset-password"
                            className="text-[14px] text-gray-500 hover:text-black font-bold"
                        >
                            {t("resetPassword")}
                        </a>
                    </div>
                </div>

                <button
                    type="submit"
                    className="mt-2 w-full bg-black text-[16px] text-white py-2 rounded-[20px] font-semibold hover:text-[#ED7C22] hover:bg-black/90 transition"
                >
                    {t("login")}
                </button>

                <LoginProviders />
            </form>
        </div>
    );
}
