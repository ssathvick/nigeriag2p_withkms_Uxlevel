"use client";
import React from "react";
import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";

interface ModalProps {
    title: React.ReactNode;
    onClose: () => void;
    children: React.ReactNode;
    width?: string;
    height?: string;
    sidebarWidth?: string;
    sidebarImage?: string;
    paddingXClass?: string;
}

export default function Modal({
    title,
    onClose,
    children,
    width = "800px",
    height = "500px",
    sidebarWidth = "25%",
    sidebarImage,
    paddingXClass = "px-10",
}: ModalProps) {
    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
            <div
                className="bg-white rounded-[20px] overflow-hidden flex shadow-lg"
                style={{ width, height }}
            >
                <div
                    className="bg-[#FBBF00] h-full flex items-start justify-center pt-8"
                    style={{ width: sidebarWidth }}
                >
                    {sidebarImage && (
                        <Image
                            src={prefixBasePath(sidebarImage)}
                            alt="Sidebar"
                            width={122}
                            height={120}
                            className="object-contain"
                            priority
                        />
                    )}
                </div>

                <div className="flex-1 flex flex-col relative">
                    <div className={`flex justify-between items-center pt-8 mb-6 ${paddingXClass}`}>
                        <h2 className="text-xl font-bold text-gray-800">{title}</h2>
                        <button onClick={onClose}>
                            <Image
                                src={prefixBasePath("/close.png")}
                                alt="Close"
                                width={20}
                                height={20}
                                className="opacity-50"
                                priority
                            />
                        </button>
                    </div>
                    <div className="flex-1 overflow-y-auto">{children}</div>
                </div>
            </div>
        </div>
    );
}
