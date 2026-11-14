"use client";
import Image from "next/image";
import { prefixBasePath } from '@/shared';

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
    const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

    return (
        <div className="flex justify-left items-center space-x-2 py-4">
            <button
                onClick={() => onPageChange(Math.max(currentPage - 1, 1))}
                className="flex items-center justify-center w-6 h-6 bg-[#D9D9D9] rounded hover:bg-gray-300"
            >
                <Image
                    src={prefixBasePath("/right_arrow.png")}
                    alt="prev"
                    width={12}
                    height={12}
                    className="transform scale-x-[-1]"
                />
            </button>

            {pages.map((page) => (
                <button
                    key={page}
                    onClick={() => onPageChange(page)}
                    className={`w-6 h-6 rounded font-medium flex items-center justify-center ${page === currentPage
                        ? "bg-black text-white"
                        : "bg-[#D9D9D9] text-black hover:bg-gray-300"
                        }`}
                >
                    {page}
                </button>
            ))}

            <button
                onClick={() => onPageChange(Math.min(currentPage + 1, totalPages))}
                className="flex items-center justify-center w-6 h-6 bg-[#D9D9D9] rounded hover:bg-gray-300"
            >
                <Image
                    src={prefixBasePath("/right_arrow.png")}
                    alt="next"
                    width={12}
                    height={12}
                />
            </button>
        </div>
    );
}
