"use client";

import { useEffect, useState } from "react";
import { getDisbursementSummaryTillDate, transformDisbursementSummary } from "@/features/disbursement/utils";
import {
    BenefitCardData,
    DisbursementItem,
} from "@/features/disbursement/types";
import { useBridgeUrl } from "@/features/disbursement/hooks/useBridgeUrl";

export function useDisbursementSummary() {
    const bridgeUrl = useBridgeUrl();

    const [benefits, setBenefits] = useState<BenefitCardData[]>([]);
    const [loading, setLoading] = useState(true);

    async function fetchSummary(baseUrl: string) {
        try {
            setLoading(true);

            const result = await getDisbursementSummaryTillDate(baseUrl);
            const list: DisbursementItem[] =
                result?.response_body?.response_payload ?? [];

            const summary = transformDisbursementSummary(list);

            setBenefits([
                { icon: "/digital_cash.png", value: summary.digital_cash, label: "Digital Cash" },
                { icon: "/physical_cash.png", value: summary.physical_cash, label: "Physical Cash" },
                { icon: "/commodity.png", value: summary.commodity, label: "Commodity" },
                { icon: "/service.png", value: summary.service, label: "Service" },
            ]);

        } catch (err) {
            console.error("Failed to fetch summary:", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (!bridgeUrl) return;
        fetchSummary(bridgeUrl);
    }, [bridgeUrl]);

    return {
        benefits,
        loading,
    };
}
