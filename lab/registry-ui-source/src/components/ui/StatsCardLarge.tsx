"use client";

import {useStatsShortcut} from '@/components/shared/StatsShortcut';
import {InfoHint} from '@/components/shared/Workflow';
import { useMemo } from "react";
import { useFetch } from "@/shared/hooks/useFetch";
import { useTranslations } from 'next-intl';
import Image from "next/image";

interface StatsCardLargeProps {
    stats_endpoint: string;
    active?: boolean;
}

const StatsCardLarge = ({
    stats_endpoint,
    active = false,
}: StatsCardLargeProps) => {
    const t = useTranslations();
    const navigate=useStatsShortcut(stats_endpoint);
    const { data, loading, error } = useFetch<any>({
        url: stats_endpoint,
    });

    const { title, rows } = useMemo(() => {
        if (loading) return { title: '', rows: [] };
        if (!data) return { title: t('items'), rows: [] };

        if (Array.isArray(data)) {
            return {
                title: t('registers'),
                rows: data.slice(0, 4).map((item) => ({
                    id: item.register_id,
                    label: t(item.register_subject),
                    value: item.total_record_count,
                    imageUrl: item.register_icon?.startsWith('data:') ? item.register_icon : undefined,
                })),
            };
        }

        if (stats_endpoint.includes("change")) {
            return {
                title: t('change_requests'),
                rows: [
                    {
                        id: "approved",
                        label: t('approved'),
                        value: data.approved_count,
                        imageUrl: "/images/register/statsIcon/approved.png",
                    },
                    {
                        id: "pending",
                        label: t('pending'),
                        value: data.pending_count,
                        imageUrl: "/images/register/statsIcon/pending.png",
                    },
                ],
            };
        }

        return { title: t('items'), rows: [] };
    }, [data, loading, stats_endpoint, t]);

    const totalCount = useMemo(() => {
        if (stats_endpoint.includes("register")) {
            return data?.length || 0;
        }
        if (stats_endpoint.includes("change")) {
            return data?.total_count || 0;
        }
    }, [data, stats_endpoint]);

    const pulseBg = active ? "bg-neutral-second/20" : "bg-neutral-first/20";

    return (
        <div className={`flex justify-between transition-all duration-200 w-full h-52 rounded-[10px] px-10 py-8 gap-2
            ${active
                ? "border-black bg-neutral-first text-neutral-second"
                : "bg-secondary-second text-secondary-third"
            }`}
        >
            {/* LEFT */}
            <div className="flex flex-col justify-center">
                {loading ? (
                    <div className="animate-pulse space-y-3">
                        <div className={`h-20 w-32 rounded ${pulseBg}`} />
                        <div className={`h-6 w-40 rounded ${pulseBg}`} />
                    </div>
                ) : (
                    <>
                        <span className="font-roboto text-[85px] font-bold leading-none">
                            <button type="button" aria-label={`View ${title}`} onClick={e=>{e.stopPropagation();navigate()}} className="rounded-full px-2 hover:bg-primary-first/30">{(totalCount || 0).toString()}</button>
                        </span>
                        <span className="font-roboto text-[24px] font-bold leading-none">
                            {title}
                        </span>
                    </>
                )}
            </div>

            {/* RIGHT */}
            <div className="flex flex-col justify-center space-y-3 min-w-35">
                {loading ? (
                    <div className="animate-pulse space-y-2">
                        <div className={`h-4 w-28 rounded ${pulseBg}`} />
                        <div className={`h-4 w-24 rounded ${pulseBg}`} />
                    </div>
                ) : error ? (
                    <p className="text-[16px] text-toast-failed">{t('failed_to_load')}</p>
                ) : (
                    rows.map((row) => (
                        <div key={row.id} className="flex items-center gap-3">
                            {row.imageUrl && (
                                <Image
                                    src={row.imageUrl}
                                    width={20}
                                    height={20}
                                    alt=""
                                    className={active ? "invert" : ""}
                                />
                            )}
                            <span className="text-[16px] font-medium leading-7.5">
                                <button type="button" aria-label={`View ${row.value || 0} ${row.label}`} onClick={e=>{e.stopPropagation();navigate(row.id)}} className={`rounded-full px-3 py-1 hover:bg-primary-first ${Number(row.value)>0 && row.id==='pending'?'bg-red-100 text-red-800':'bg-secondary-first text-secondary-third'}`}>{(row.value || 0).toString()}</button>
                            </span>
                            <span className="text-[16px] font-medium leading-7.5 opacity-80">
                                {row.label}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default StatsCardLarge;
