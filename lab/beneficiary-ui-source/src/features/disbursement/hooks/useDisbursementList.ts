"use client";

import { getAllDisbursements } from "@/features/disbursement/utils";
import { DisbursementRecord } from "@/features/disbursement/types";
import { useBridgeUrl } from "@/features/disbursement/hooks";
import { usePaginatedData } from "@/shared/hooks/usePaginatedData";

export function useDisbursementList(currentPage: number, pageSize = 8) {
    const bridgeUrl = useBridgeUrl();

    const result = usePaginatedData<DisbursementRecord>({
        baseUrl: bridgeUrl,
        currentPage,
        pageSize,
        fetchFn: getAllDisbursements,
    });

    return {
        disbursements: result.data,
        loading: result.loading,
        totalPages: result.totalPages,
        totalItems: result.totalItems,
    };
}
