"use client";
import { useState } from "react";
import { useLocale } from "next-intl";
import { AuthUtil } from "@/features/auth/components";
import { Loading, Pagination, SearchInput } from "@/components/shared";
import { NewsDetails } from "@/features/news/components";
import { News } from "@/features/news/types";
import { useNews } from "@/features/news/hooks/useNews";
import { getMediaUrl } from "@/features/news/utils/utils";

export default function NewsPage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const pageSize = 5;
    const [currentPage, setCurrentPage] = useState(1);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedNews, setSelectedNews] = useState<News | null>(null);

    const { news, total, loading } = useNews(
        currentPage,
        pageSize,
        searchQuery
    );

    const totalPages = Math.ceil(total / pageSize);

    if (loading) {
        return <Loading title={"Latest News"} height={"655px"} />
    }

    return (
        <div className="px-[50px] py-4 min-h-screen bg-white">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-4">
                Latest News
            </h1>

            <div className="bg-white overflow-hidden rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)]">
                <div className="mb-4 px-6 pt-4 flex items-center justify-between">
                    <h2 className="text-[20px] font-[600] text-[#ED7C22]">All News</h2>
                    <SearchInput
                        onSearch={(val) => {
                            setCurrentPage(1);
                            setSearchQuery(val);
                        }}
                        placeholder="Search"
                        className="w-[200px]"
                    />
                </div>

                <div className="flex flex-col divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
                    {news.map((n, idx) => (
                        <div
                            key={n.id}
                            onClick={() => setSelectedNews(n)}
                            className={`${idx % 2 === 0 ? "bg-gray-100" : "bg-white"} cursor-pointer`}
                        >
                            <div className="flex gap-3 px-6 py-3">
                                <div className="flex-shrink-0 w-16 h-16">
                                    <img
                                        src={getMediaUrl(n.image?.url)}
                                        alt={n.image?.alternativeText || n.title}
                                        className="w-full h-full object-contain rounded-md bg-white"
                                    />
                                </div>

                                <div className="flex-1 min-w-0">
                                    <h3 className="text-[18px] font-[500] text-black truncate">{n.title}</h3>
                                    {n.date && (
                                        <span className="text-[14px] text-[#3399FF] block mt-0.5">
                                            {new Date(n.date).toLocaleString()}
                                        </span>
                                    )}
                                    <p className="text-sm text-gray-700 mt-1 line-clamp-1">
                                        {n.description}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}

                    {Array.from({ length: pageSize - news.length }).map((_, idx) => (
                        <div
                            key={`empty-${idx}`}
                            className={`${(news.length + idx) % 2 === 0 ? "bg-gray-100" : "bg-white"}`}
                        >
                            <div className="flex gap-3 px-6 py-[17px]">
                                <div className="w-16 h-16 bg-transparent" />
                                <div className="flex-1 py-3">&nbsp;</div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex items-center gap-6 px-8 py-4 text-sm text-black">
                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setCurrentPage}
                    />
                    <div className="text-gray-600">
                        Showing {(currentPage - 1) * pageSize + 1}-
                        {Math.min(currentPage * pageSize, total)} of {total} news
                    </div>
                </div>
            </div>
            {selectedNews && (
                <NewsDetails news={selectedNews} onClose={() => setSelectedNews(null)} />
            )}
        </div>
    );
}
