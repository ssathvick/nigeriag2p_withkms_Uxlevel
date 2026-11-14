"use client";

export default function NewsCardLoading() {
    return (
        <>
            {Array(3)
                .fill(0)
                .map((_, index) => (
                    <div
                        key={`loading-${index}`}
                        className={`${index % 2 === 0 ? "bg-[#F5F5F5]" : ""} animate-pulse`}
                    >
                        <div className="flex gap-4 px-8 py-4">
                            <div className="w-10 h-10 rounded-md bg-gray-300"></div>
                            <div className="flex-1">
                                <div className="lg:h-5 xl:h-5 2xl:h-5 bg-gray-200 rounded w-3/4 mb-1"></div>
                                <div className="lg:h-4 xl:h-4 2xl:h-4 bg-gray-200 rounded w-full"></div>
                                <div className="lg:h-3 xl:h-3 2xl:h-4 bg-gray-200 rounded w-2/3 mt-1"></div>
                            </div>
                        </div>
                    </div>
                ))}
        </>
    );
}
