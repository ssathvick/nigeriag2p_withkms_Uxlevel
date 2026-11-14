"use client";
import { useLocale } from "next-intl";
import Image from "next/image";

import { AuthUtil, LoginForm } from '@/features/auth/components';
import { prefixBasePath } from '@/shared/utils/path';

export default function LoginPage() {
    const lang = useLocale();
    return (
        <div className="relative h-screen bg-white flex items-center justify-center overflow-hidden">
            <AuthUtil successRedirectUrl={`/${lang}/dashboard`} />

            <div className="relative w-full max-w-[1600px] h-full max-h-[800px] mx-auto px-4">
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
                    <LoginForm />
                </div>

                <div className="absolute inset-0 -translate-x-[3%]">
                    <Image
                        src={prefixBasePath("/02_login.png")}
                        alt="Decoration"
                        width={200}
                        height={200}
                        className="absolute top-[25.38%] left-[22.5%] w-[12.5%] h-auto rounded-xl shadow-lg"
                    />
                    <Image
                        src={prefixBasePath("/04_login.png")}
                        alt="Decoration"
                        width={110}
                        height={115}
                        className="absolute top-[42%] left-[13.75%] w-[6.88%] h-auto rounded-xl shadow-lg"
                    />
                    <Image
                        src={prefixBasePath("/05_login.png")}
                        alt="Decoration"
                        width={260}
                        height={159}
                        className="absolute top-[53.38%] left-[21.25%] w-[16.25%] h-auto rounded-xl shadow-lg"
                    />

                    <Image
                        src={prefixBasePath("/01_login.png")}
                        alt="Decoration"
                        width={200}
                        height={210}
                        className="absolute top-[24.13%] left-[70%] w-[12.5%] h-auto rounded-xl shadow-lg"
                    />
                    <Image
                        src={prefixBasePath("/03_login.png")}
                        alt="Decoration"
                        width={120}
                        height={120}
                        className="absolute top-[40.13%] left-[84.5%] w-[7.5%] h-auto rounded-xl shadow-lg"
                    />
                    <Image
                        src={prefixBasePath("/06_login.png")}
                        alt="Decoration"
                        width={260}
                        height={150}
                        className="absolute top-[54.5%] left-[73.13%] w-[16.25%] h-auto rounded-xl shadow-lg"
                    />
                </div>
            </div>
        </div>
    );
}
