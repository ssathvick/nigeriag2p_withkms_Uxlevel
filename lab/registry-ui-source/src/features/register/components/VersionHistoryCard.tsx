'use client';

import ViewAll from "@/components/shared/ViewAll";
import { useFetch } from "@/shared/hooks/useFetch";
import { useLocale, useTranslations } from "next-intl";
import Image from "next/image";

interface Props {
    type: string;
    registerId: string;
    internalRecordId: string;
    activeTabId?: string;
}

export default function VersionHistoryCard({
    type,
    registerId,
    internalRecordId,
    activeTabId
}: Props) {
    const locale = useLocale();
    const t = useTranslations();

    const { data, loading } = useFetch<any>({
        url: `/api/register/versions`,
        enabled: !!registerId && !!internalRecordId && !!activeTabId,
        options: {
            method: "POST",
            body: JSON.stringify({
                register_id: registerId,
                internal_record_id: internalRecordId,
                tab_id: activeTabId
            }),
        },
    });

    const payload =
        data as
        | {
            number_of_versions: number;
            last_updated_by: string;
            last_updated_at: string;
            last_approved_by?: string;
            last_approved_at?: string;
        }
        | undefined;

    if (loading) {
        return (
            <div className="relative rounded-[10px] bg-secondary-second px-7.25 pt-5 pb-7.25 overflow-hidden animate-pulse">
                <div className="flex items-center justify-between mb-5">
                    <div className="h-6 w-40 rounded bg-neutral-first/20" />
                    <div className="h-15 w-20 rounded-[20px] bg-neutral-first/20" />
                </div>

                <div className="space-y-3">
                    <div className="h-4 w-32 rounded bg-neutral-first/20" />
                    <div className="h-4 w-64 rounded bg-neutral-first/20" />
                </div>

                <div className="mt-4 space-y-3">
                    <div className="h-4 w-32 rounded bg-neutral-first/20" />
                    <div className="h-4 w-64 rounded bg-neutral-first/20" />
                </div>

                <div className="mt-6 h-10 w-32 rounded-full bg-neutral-first/20" />
            </div>
        );
    }

    if (!payload) return null;

    const params = new URLSearchParams();
    if (activeTabId) params.set("tab", activeTabId);

    const href = `/${locale}/register/${type}/${internalRecordId}/version-history${params.toString() ? `?${params.toString()}` : ""
        }`;

    const count = payload.number_of_versions ?? 0;

    const isDisabled = count === 0;

    return (
        <div className="relative rounded-[10px] bg-secondary-second px-7.25 pt-5 pb-7.25 overflow-hidden">
            <div className="flex items-center justify-between mb-5">
                <h3 className="text-[24px] font-semibold text-neutral-first leading-none">
                    {t("version_history")}
                </h3>
                <div className="flex h-15 w-20 items-center justify-center rounded-[10px] border-3 border-white bg-secondary-second text-[34px] font-bold text-neutral-first">
                    {count.toString().padStart(2, '0')}
                </div>
            </div>

            <div className="space-y-1 text-[16px] text-neutral-first font-normal">
                <p className="font-medium">{t("last_updated_by")}</p>
                <div className="flex items-center gap-2">
                    <Image
                        src="/images/register/version_profile.png"
                        alt="Updated by"
                        width={16}
                        height={16}
                        className="rounded-full"
                    />
                    <span>{payload.last_updated_by}</span>
                    <Image
                        src="/images/register/version_calendar.png"
                        alt="Date"
                        width={14}
                        height={14}
                        className="ml-2"
                    />
                    <span>
                        {new Date(payload.last_updated_at).toLocaleDateString()}
                    </span>
                </div>
            </div>

            {payload.last_approved_by && payload.last_approved_at && (
                <div className="mt-4 space-y-1 text-[16px] text-neutral-first">
                    <p className="font-medium">{t("last_approved_by")}</p>
                    <div className="flex items-center gap-2">
                        <Image
                            src="/images/register/version_profile.png"
                            alt="Approved by"
                            width={16}
                            height={16}
                            className="rounded-full"
                        />
                        <span>{payload.last_approved_by}</span>
                        <Image
                            src="/images/register/version_calendar.png"
                            alt="Date"
                            width={14}
                            height={14}
                            className="ml-2"
                        />
                        <span>
                            {new Date(payload.last_approved_at).toLocaleDateString()}
                        </span>
                    </div>
                </div>
            )}
            <div
                className={isDisabled ? "invisible cursor-not-allowed pointer-events-none" : ""}
            >
                <ViewAll
                    href={href}
                    bgColor="var(--color-secondary-third)"
                    label={t("know_more")}
                />
            </div>
        </div>
    );
}
