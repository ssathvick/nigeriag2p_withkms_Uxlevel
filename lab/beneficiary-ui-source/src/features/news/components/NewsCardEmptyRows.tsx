"use client";

interface Props {
    count: number;
    offset?: number;
}

export default function NewsCardEmptyRows({ count, offset = 0 }: Props) {
    return (
        <>
            {Array(count)
                .fill(0)
                .map((_, index) => {
                    const listIndex = offset + index;
                    return (
                        <div
                            key={`empty-${index}`}
                            className={`${listIndex % 2 === 0 ? "bg-[#F5F5F5]" : ""}`}
                        >
                            <div className="flex gap-4 px-8 py-4">
                                <div className="w-10 h-10 rounded-md bg-transparent"></div>
                                <div className="flex-1">
                                    <div className="h-4 bg-transparent w-3/4 mb-1"></div>
                                    <div className="h-4 bg-transparent w-full"></div>
                                    <div className="h-4 bg-transparent w-2/3 mt-1"></div>
                                </div>
                            </div>
                        </div>
                    );
                })}
        </>
    );
}
