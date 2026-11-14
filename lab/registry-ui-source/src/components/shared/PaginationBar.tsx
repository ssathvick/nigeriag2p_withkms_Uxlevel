"use client";

import Image from "next/image";

interface PaginationBarProps {
    pageStart: number;
    pageEnd: number;
    total: number;
    onPrev: () => void;
    onNext: () => void;
}

const formatNumber = (num: number) => {
    if (num < 1000) return num.toString();
    if (num >= 1000000000) {
        const val = num / 1000000000;
        return `${val < 10 ? val.toFixed(1).replace(/\.0$/, "") : Math.floor(val)}B`;
    }
    if (num >= 1000000) {
        const val = num / 1000000;
        return `${val < 10 ? val.toFixed(1).replace(/\.0$/, "") : Math.floor(val)}M`;
    }
    const val = num / 1000;
    return `${val < 10 ? val.toFixed(1).replace(/\.0$/, "") : Math.floor(val)}k`;
};

export default function PaginationBar({
    pageStart,
    pageEnd,
    total,
    onPrev,
    onNext,
}: PaginationBarProps) {
    const isPrevDisabled = pageStart <= 1;
    const isNextDisabled = pageEnd >= total;

    return (
        <div className="flex items-center gap-2">
            <span className="min-w-20 px-2 h-4.75 text-center font-normal text-[16px] text-neutral-first whitespace-nowrap">
                {formatNumber(pageStart)} - {formatNumber(pageEnd)} of {formatNumber(total)}
            </span>


            <div className="flex items-center gap-2">
                <button
                    onClick={onPrev}
                    disabled={isPrevDisabled}
                    className={`w-10 h-8.5 flex items-center justify-center rounded-[10px]
            ${isPrevDisabled
                            ? "bg-primary-first cursor-not-allowed"
                            : "bg-primary-first"
                        }`}
                >
                    <Image
                        src="/images/common/arrow_back_01.png"
                        width={12}
                        height={12}
                        alt="prev"
                    />
                </button>

                <button
                    onClick={onNext}
                    disabled={isNextDisabled}
                    className={`w-10 h-8.5 flex items-center justify-center rounded-[10px]
            ${isNextDisabled
                            ? "bg-primary-first cursor-not-allowed"
                            : "bg-primary-first"
                        }`}
                >
                    <Image
                        src="/images/common/arrow_next_01.png"
                        width={12}
                        height={12}
                        alt="next"
                    />
                </button>
            </div>
        </div>
    );
}
