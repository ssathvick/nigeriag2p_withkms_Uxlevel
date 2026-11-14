import { apiRequest } from "@/shared/utils/apiRequest";
import { buildStandardPayload, PaginationParams } from "@/shared/utils/payloadBuilder";

export function getAllDisbursements(baseUrl: string, params: PaginationParams = {}) {
    return apiRequest(
        baseUrl,
        "/disbursement/get_all_disbursements",
        buildStandardPayload(params)
    );
}

export function getDisbursementSummaryTillDate(
    baseUrl: string,
    extraPayload: Record<string, any> = {}
) {
    return apiRequest(
        baseUrl,
        "/disbursement/get_disbursement_summary_till_date",
        buildStandardPayload({ extraPayload })
    );
}
