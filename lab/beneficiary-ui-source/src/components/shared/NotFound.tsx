"use client";
import Image from "next/image";

import "@/commons/globals.css";
import { GlobalContextProvider } from "@/context/GlobalContext";
import { prefixBasePath } from "@/shared/utils/path";

export default function NotFoundClient() {
    return (
        <html lang="en">
            <body>
                <GlobalContextProvider>
                    <main className="bg-white flex flex-col items-center justify-center min-h-screen font-fontcustom px-4 text-center">
                        <Image
                            src={prefixBasePath("/404.png")}
                            alt="404 Not Found"
                            width={150}
                            height={150}
                            className="rounded-xl"
                        />

                        <h1 className="text-[50px] font-[500] text-[#ED7C22]">
                            Oops!
                        </h1>

                        <p className="text-gray-600 text-[15px] leading-6 mb-6">
                            404 Error, sorry we couldn't find that page.
                        </p>

                        <button
                            onClick={() => window.history.back()}
                            className="bg-black text-white px-6 py-2 rounded-[20px]"
                        >
                            GO BACK
                        </button>
                    </main>
                </GlobalContextProvider>
            </body>
        </html>
    );
}
