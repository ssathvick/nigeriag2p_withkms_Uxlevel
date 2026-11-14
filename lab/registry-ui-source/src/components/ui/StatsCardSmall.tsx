"use client";

import {useStatsShortcut} from '@/components/shared/StatsShortcut';
import {InfoHint} from '@/components/shared/Workflow';
import { useMemo } from "react";
import { useFetch } from "@/shared/hooks/useFetch";
import { useTranslations } from 'next-intl';
import Image from "next/image";

interface StatsCardSmallProps {
    stats_endpoint: string;
    active?: boolean;
}

const StatsCardSmall = ({
    stats_endpoint,
    active = false,
}: StatsCardSmallProps) => {
    const t = useTranslations();
    const navigate=useStatsShortcut(stats_endpoint);
    const { data, loading, error } = useFetch<any>({
        url: stats_endpoint,
    });

    const { title, rows } = useMemo(() => {
        if (!data) return { title: t('items'), rows: [] };

        if (Array.isArray(data)) {
            return {
                title: t('registers'),
                rows: data.slice(0, 2).map((item) => ({
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

        if (stats_endpoint.includes("intake")) {
            return {
                title: 'Form Submissions',
                rows: [
                    {
                        id: "pendingSubmissions",
                        label: t('pending_submissions'),
                        value: data.total_approval_pending_submissions,
                        imageUrl: "/images/register/statsIcon/topics.png",
                    },
                    {
                        id: "draftSubmissions",
                        label: t('draft_submissions'),
                        value: data.total_draft_submissions,
                        imageUrl: "/images/register/statsIcon/data_models.png",
                    },
                ],
            };
        }

        if (stats_endpoint.includes("messages")) {
            return {
                title: t('messages'),
                rows: [
                    {
                        id: "incomingMessages",
                        label: t('incoming_messages'),
                        value: data.no_of_messages|| "0",
                        imageUrl: "/images/messages/message_icon.png",
                    },
                    {
                        id: "outgoingMessages",
                        label: t('outgoing_messages'),
                        value: data.outgoing || "0",
                        imageUrl: "/images/messages/message_icon.png",
                    },
                ],
            };
        }

        if (stats_endpoint.includes("/tasks")) {
            return {
                title: 'My Tasks',
                rows: [
                    {
                        id: "change_request",
                        label: t('change_requests'),
                        value: data.change_request_count,
                        imageUrl: "/images/register/statsIcon/pending.png",
                    },
                    {
                        id: "intake_form",
                        label: t('intake_submissions'),
                        value: data.intake_form_count,
                        imageUrl: "/images/register/statsIcon/topics.png",
                    },
                ],
            };
        }

        return { title: t('items'), rows: [] };
    }, [data, stats_endpoint, t]);

    const totalCount = useMemo(() => {
        // For registers, just count how many registers
        if (stats_endpoint.includes("register")) {
            return data?.length || 0;
        }
        if (stats_endpoint.includes("change")) {
            return data?.total_count || 0;
        }
        if (stats_endpoint.includes("intake")) {
            return data?.total_submissions || 0;
        }
        if (stats_endpoint.includes("messages")) {
            return data?.no_of_messages || 0;
        }
        if (stats_endpoint.includes("/tasks")) {
            return data?.total || 0;
        }
    }, [data, stats_endpoint]);

    return (
        <div className={`flex flex-col justify-between  transition-all duration-200 w-full rounded-[10px] px-7 py-6 ${active ? "border-black bg-neutral-first text-neutral-second" : "bg-secondary-second text-secondary-third"}`}>
            <div className="min-h-40">
                {/* count and title */}
                <div className="mb-4 mt-4">
                    {loading ? (
                        <div className="animate-pulse space-y-2">
                            <div className="h-12.5 w-32 rounded bg-secondary-third dark:bg-secondary-second-700"></div>
                            <div className="h-7 w-24 rounded bg-secondary-third dark:bg-secondary-second-700"></div>
                        </div>
                    ) : (
                        <>
                            <h2 className="font-roboto text-[45px] font-bold leading-none truncate overflow-hidden whitespace-nowrap" title={totalCount}>
                                <button type="button" aria-label={`View ${title}`} onClick={e=>{e.stopPropagation();navigate()}} className="rounded-full px-2 hover:bg-primary-first/30 focus-visible:outline-2">{totalCount}</button>
                            </h2>
                            <h3 className="font-roboto text-[22px] font-bold leading-7 truncate overflow-hidden whitespace-nowrap" title={title}>
                                {title}<InfoHint text={stats_endpoint.includes('tasks')?'Your pending review tasks. Open the intake or change-request count to view that exact queue.':stats_endpoint.includes('intake')?'Saved intake forms and their current review status. Select a count to open its filtered list.':stats_endpoint.includes('change')?'Changes proposed for existing master records. Open a count to view the corresponding approval status.':'Approved household and individual records. Select a count to open that master register.'}/>
                            </h3>
                        </>
                    )}
                </div>


                {loading ? (
                    <div className="animate-pulse">
                        <div className="h-4 w-24 rounded bg-secondary-third dark:bg-secondary-second-700 mb-1.75"></div>
                        <div className="h-5 w-32 rounded bg-secondary-third dark:bg-secondary-second-700"></div>
                    </div>
                ) : error ? (
                    <p className="text-sm text-toast-failed">{t('failed_to_load')}</p>
                ) : (
                    // items
                    <ul>
                        {rows.map((row) => (
                            <li key={row.id} className="flex items-center gap-2">
                                {row.imageUrl && (
                                    <Image
                                        src={row.imageUrl}
                                        width={20}
                                        height={20}
                                        alt=""
                                        className={active ? "invert" : "opacity-60"}
                                    />
                                )}

                                {/* value */}
                                <button type="button" onClick={e=>{e.stopPropagation();navigate(row.id)}} aria-label={`View ${row.value || 0} ${row.label}`} className={`rounded-full px-3 py-0.5 font-bold transition-colors hover:bg-primary-first hover:text-neutral-first ${Number(row.value)>0 && (stats_endpoint.includes('tasks') || row.id==='pending' || row.id==='pendingSubmissions' || row.id==='draftSubmissions')?'bg-red-100 text-red-800':'bg-secondary-first text-secondary-third'}`}>{row.value || 0}</button>

                                {/* label */}
                                <span className="font-roboto text-[16px] font-medium leading-7 opacity-80 truncate overflow-hidden whitespace-nowrap" title={row.label}>
                                    {row.label}
                                </span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default StatsCardSmall;
