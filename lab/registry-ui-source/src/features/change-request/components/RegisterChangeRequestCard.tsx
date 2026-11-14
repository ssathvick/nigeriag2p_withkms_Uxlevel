import ViewAll from "@/components/shared/ViewAll";
import { useFetch } from "@/shared/hooks/useFetch";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { useEffect, useRef } from "react";

interface Props {
    registerId: string;
    internalRecordId: string;
    type: string;
    activeTabId?: string;
    count?: number;
    onCountLoaded?: (count: number) => void;
}

export default function RegisterChangeRequestCard({
    type,
    registerId,
    internalRecordId,
    activeTabId,
    count: externalCount,
    onCountLoaded,
}: Props) {
    const locale = useLocale();
    const t = useTranslations();
    const hasLoadedInitialCount = useRef(false);

    const { data, loading } = useFetch<any>({
        url: `/api/change-request/pending`,
        enabled: !!registerId && !!internalRecordId && !!activeTabId,
        options: {
            method: "POST",
            body: JSON.stringify({
                subject_register_id: registerId,
                subject_record_id: internalRecordId,
                tab_id: activeTabId,
            }),
        },
    });

    // Initialize parent state with API data on first load
    useEffect(() => {
        if (!hasLoadedInitialCount.current && data?.number_of_pending_change_requests !== undefined && onCountLoaded) {
            onCountLoaded(data.number_of_pending_change_requests);
            hasLoadedInitialCount.current = true;
        }
    }, [data, onCountLoaded]);

    // Use external count if provided, otherwise use API data
    const count = externalCount ?? data?.number_of_pending_change_requests ?? 0;

    const isDisabled = count === 0;

    const params = new URLSearchParams();
    if (activeTabId) params.set("tab", activeTabId);

    const href = `/${locale}/register/${type}/${internalRecordId}/change-request${params.toString() ? `?${params.toString()}` : ""
        }`;

    if (loading) {
        return (
            <div className="relative rounded-[10px] bg-primary-first px-7.25 pt-4 pb-7.25 overflow-hidden animate-pulse">
                <div className="flex items-center justify-between">
                    <div className="h-6 w-40 rounded bg-neutral-first/20" />
                    <div className="h-15 w-20 rounded-[20px] bg-neutral-first/20" />
                </div>

                <div className="mt-3 h-3 w-56 rounded bg-neutral-first/20" />

                <div className="mt-25 h-10 w-32 rounded-full bg-neutral-first/20" />

                <div className="absolute bottom-4 right-4 h-30 w-30 rounded-full bg-neutral-first/20" />
            </div>
        );
    }

    return (
        <div className="relative rounded-[10px] bg-primary-first px-7.25 pt-5 pb-7.25 overflow-hidden">
            <div className="flex items-center justify-between">
                <h3 className="text-[24px] font-semibold text-neutral-first leading-none">
                    {t("change_request")}
                </h3>
                <div className="flex h-15 w-20 items-center justify-center rounded-[10px] border-3 border-white bg-primary-first text-[34px] font-bold text-neutral-first">
                    {count.toString().padStart(2, '0')}
                </div>
            </div>

            <p className="mt-3 text-[16px] text-neutral-first font-normal">
                {count > 0
                    ? t("pending_changes")
                    : t("no_pending_changes")}
            </p>

            <div className="mt-25">
                <div
                    className={isDisabled ? "invisible cursor-not-allowed pointer-events-none" : ""}
                >
                    <ViewAll
                        href={href}
                        bgColor="var(--color-secondary-second)"
                        label={t("know_more")}
                    />
                </div>
                <Image
                    src="/images/changerequest/cr.png"
                    alt="Change Request"
                    width={164}
                    height={164}
                    className="absolute bottom-0 right-2"
                />
            </div>
        </div>
    );
}
