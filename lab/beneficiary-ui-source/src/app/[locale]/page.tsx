"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";

import { prefixBasePath } from '@/shared/utils/path';


export default function HomePage() {
    const router = useRouter();
    const locale = useLocale();
    const t = useTranslations("homePage");
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("authToken");
        setIsLoggedIn(!!token);
    }, []);

    const handleGetStarted = () => {
        if (isLoggedIn) {
            router.push(`/${locale}/dashboard`);
        } else {
            router.push(`/${locale}/login`);
        }
    };

    return (
        <main className="relative h-screen w-full overflow-hidden flex items-center justify-center bg-gradient-to-br from-black via-[#202020] to-[#939292]">
            <div className="relative w-full max-w-[1440px] h-full max-h-[900px] mx-auto px-4">
                <div className="absolute top-[5.44%] left-[31.74%] w-[61.81%] h-[77%]">
                    <div className="absolute top-[39.1%] left-[18.24%] w-[20.79%]">
                        <Image
                            src={prefixBasePath("/02_landing.png")}
                            alt="Decoration"
                            width={185}
                            height={156}
                            className="w-full h-auto object-cover rounded-lg shadow-lg"
                        />
                    </div>

                    <div className="absolute top-[66.09%] left-[42.39%] w-[15.17%]">
                        <Image
                            src={prefixBasePath("/05_landing.png")}
                            alt="Decoration"
                            width={135}
                            height={145}
                            className="w-full h-auto object-cover rounded-lg shadow-lg"
                        />
                    </div>

                    <div className="absolute top-[67.97%] left-7 w-[30.9%]">
                        <Image
                            src={prefixBasePath("/06_landing.png")}
                            alt="Decoration"
                            width={275}
                            height={181}
                            className="w-full h-auto object-cover rounded-lg shadow-lg"
                        />
                    </div>

                    <div className="absolute top-0 left-[43.52%] w-[41.57%]">
                        <Image
                            src={prefixBasePath("/01_landing.png")}
                            alt="Decoration"
                            width={370}
                            height={353}
                            className="w-full h-auto object-cover rounded-lg shadow-lg"
                        />
                    </div>

                    <div className="absolute top-[26.41%] left-[89.58%] w-[15.17%]">
                        <Image
                            src={prefixBasePath("/04_landing.png")}
                            alt="Decoration"
                            width={135}
                            height={130}
                            className="w-full h-auto object-cover rounded-lg shadow-lg"
                        />
                    </div>

                    <div className="absolute top-[53.54%] left-[62.06%] w-[30.9%]">
                        <Image
                            src={prefixBasePath("/03_landing.png")}
                            alt="Decoration"
                            width={275}
                            height={197}
                            className="w-full h-auto object-cover rounded-lg shadow-lg"
                        />
                    </div>

                    <div className="absolute top-[83.41%] left-[94.08%] w-[12.92%]">
                        <Image
                            src={prefixBasePath("/07_landing.png")}
                            alt="Logo"
                            width={115}
                            height={115}
                            className="w-full h-auto object-cover rounded-lg shadow-lg"
                        />
                    </div>
                </div>

                <div className="absolute top-[35%] left-[6.94%] w-[35%]">
                    <div className="mb-6">
                        <h1 className="text-white leading-[100%] text-[50px]">
                            Welcome to OpenG2P<br />
                            <span className="text-[#ED7C22] text-[50px]">Beneficiary Portal</span>
                        </h1>
                    </div>

                    <button
                        onClick={handleGetStarted}
                        className="bg-white text-black text-[20px] py-2 px-6 rounded-[30px] font-[600] flex items-center justify-center gap-2 hover:text-[#ED7C22] transition-colors duration-300"
                    >
                        GET STARTED
                        <Image
                            src={prefixBasePath("/right_arrow.png")}
                            alt="Right Arrow"
                            width={18}
                            height={18}
                        />
                    </button>
                </div>
            </div>
        </main>
    );
}
