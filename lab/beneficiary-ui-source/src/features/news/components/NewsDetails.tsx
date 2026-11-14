"use client";

import Modal from "@/components/ui/Modal";
import { News } from "@/features/news/types";

interface NewsDetailsProps {
    news: News;
    onClose: () => void;
}

export default function NewsDetails({ news, onClose }: NewsDetailsProps) {
    return (
        <Modal
            title={<span className="text-[#ED7C22] text-[24px] font-semibold">News Details</span>}
            onClose={onClose}
            width="800px"
            height="500px"
            sidebarWidth="25%"
            sidebarImage="/news_popup.png"
        >
            <div className="space-y-6 px-10 py-4">
                <div>
                    <div className="text-[18px] text-black font-semibold">
                        {news.title}
                    </div>
                    <div className="text-[16px] text-[#3399FF] font-medium">
                        {news.date}
                    </div>
                </div>

                {news.description && (
                    <div>
                        <p className="text-[16px] text-black leading-relaxed">
                            {news.description}
                        </p>
                    </div>
                )}
            </div>

            <div className="flex justify-start gap-4 w-full mt-4 px-10">
                <button
                    onClick={onClose}
                    className="px-8 py-2 bg-gray-100 text-black rounded-[20px] hover:bg-gray-200 transition"
                >
                    CLOSE
                </button>
            </div>
        </Modal>
    );
}
