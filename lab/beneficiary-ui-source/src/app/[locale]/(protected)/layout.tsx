"use client";

import { ReactNode } from "react";
import { useRouter } from "next/navigation";

import { Header, Sidebar } from '@/components/layout';

export default function ProtectedLayout({ children }: { children: ReactNode }) {
    const router = useRouter();

    const handleSidebarItemClick = (index: number, href: string) => {
        router.push(href);
    };

    return (
        <>
            <Header />
            <Sidebar onItemClick={handleSidebarItemClick} />
            <main className="transition-all duration-300 ease-in-out flex-1 pt-[70px] ml-[60px] lg:ml-[60px]">
                {children}
            </main>
        </>
    );
}
