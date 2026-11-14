"use client";

import Image from "next/image";
import { prefixBasePath } from "@/shared/utils/path";
import { ViewAll } from "@/components/shared";
import { News } from "@/features/news/types";
import { NewsCardEmptyRows, NewsCardLoading } from "@/features/news/components";
import { getMediaUrl } from "../utils/utils";


interface NewsCardProps {
    news: News[];
    loading: boolean;
}

export default function NewsCard({ news, loading }: NewsCardProps) {
    return (
        <div className="bg-white rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] flex-1 mb-[50px] mr-[50px]">
            <div className="flex items-center justify-between h-16 px-8">
                <h3 className="lg:text-[18px]/[21px] xl:text-[18px]/[21px] 2xl:text-[20px]/[23px] font-[600] text-black">
                    Latest News
                </h3>
                <button className="p-1 rounded-full hover:bg-gray-200">
                    <Image
                        src={prefixBasePath("/more.png")}
                        alt="menu"
                        width={18}
                        height={18}
                    />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
                {!loading &&
                    news.map((n, idx) => (
                        <div key={n.id} className={`${idx % 2 === 0 ? "bg-[#F5F5F5]" : ""}`}>
                            <div className="flex gap-4 px-8 py-3">
                                <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-md bg-[#FFF4EB]">
                                    <img
                                        src={getMediaUrl(n.image?.url)}
                                        alt={n.image?.alternativeText || n.title}
                                        className="w-full h-full object-contain rounded-md bg-white"
                                    />
                                </div>
                                <div className="flex-1">
                                    <h3 className="lg:text-[14px] xl:text-[14px] 2xl:text-[15px] font-[600] text-black line-clamp-1">{n.title}</h3>
                                    <p className="lg:text-[13px] xl:text-[13px] 2xl:text-[14px] text-black/50 mt-1 line-clamp-2">
                                        {n.description}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}

                {loading && <NewsCardLoading />}

                {!loading && news.length < 3 && (
                    <NewsCardEmptyRows count={3 - news.length} offset={news.length} />
                )}
            </div>

            <div className="my-3">
                {loading ? (
                    <div className="mt-3.5 mx-[30px] h-[35px] w-[180px] rounded-[15px] bg-black/20 animate-pulse"></div>
                ) : (
                    <ViewAll
                        href="/news"
                        label="View latest News"
                        bgColor="#F5F5F5"
                        hoverBgColor="#ED7C22"
                        hoverTextColor="#FFFFFF"
                    />
                )}
            </div>
        </div>
    );
}
