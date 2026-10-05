'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useTranslations } from 'next-intl';

interface MessagePopupProps {
    onClose: () => void;
    rawJson: object | null;
    transformedJson: object | null;
    enrichedJson: object | null;
    loading?: boolean;
}

export default function MessagePopup({
    onClose,
    rawJson,
    transformedJson,
    enrichedJson,
    loading,
}: MessagePopupProps) {
    const t = useTranslations();
    const [activeTab, setActiveTab] = useState(0);

    const tabs = [
        { id: 'raw', label: t('raw_message') || 'Raw Message', data: rawJson },
        { id: 'enriched', label: t('enriched_message') || 'Enriched Message', data: enrichedJson },
        { id: 'transformed', label: t('transformed_message') || 'Transformed Message', data: transformedJson },
    ];

    return (
        <div className="fixed inset-0 bg-neutral-first/80 flex justify-center items-center z-50">
            <div className="relative bg-neutral-second rounded-[10px] w-200 h-150 p-10 border-10 border-primary-first flex flex-col">
                <button
                    className="absolute top-10 right-10 opacity-50"
                    onClick={onClose}
                >
                    <Image src="/images/changerequest/cr_close.png" alt={t('close') || "Close"} width={30} height={30} />
                </button>

                <div className="pb-3">
                    <div className="flex gap-2 pr-10">
                        {tabs.map((tab, index) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(index)}
                                className={`px-8 py-2 text-[18px] font-medium rounded-t-[10px] transition-all ${activeTab === index
                                    ? 'bg-primary-first'
                                    : 'bg-secondary-second'
                                    }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex-1 bg-secondary-second/50 px-6 py-3 overflow-y-auto overflow-x-auto message-json-scroll">
                    {loading ? (
                        <div className="text-center py-10">{t('loading') || 'Loading...'}</div>
                    ) : (
                        <pre className="text-[14px] text-neutral-first whitespace-pre">
                            {JSON.stringify(tabs[activeTab]?.data, null, 2)}
                        </pre>
                    )}
                </div>

                <button
                    onClick={onClose}
                    className="mt-4 bg-neutral-first text-[16px] text-neutral-second px-10 py-2 rounded-[10px] w-fit self-start"
                >
                    {t('close') || 'Close'}
                </button>
            </div>
        </div>
    );
}
