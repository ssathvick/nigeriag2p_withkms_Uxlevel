export interface PaginationParams {
    currentPage?: number;
    pageSize?: number;
    sortBy?: string;
    filterBy?: string;
    searchText?: string;
}

export interface PayloadOptions extends PaginationParams {
    extraPayload?: Record<string, any>;
}

export function buildStandardPayload({
    currentPage = 1,
    pageSize = 8,
    sortBy = "",
    filterBy = "",
    searchText = "",
    extraPayload = {}
}: PayloadOptions = {}) {
    return {
        request_header: {
            sender_app_mnemonic: "BENEFICIARY_PORTAL",
            sender_app_url: typeof window !== "undefined" ? window.location.origin : "",
            request_id: "web-client",
            request_timestamp: new Date().toISOString(),
            instance_id: "portal-ui"
        },
        request_body: {
            pagination_request: {
                current_page: currentPage,
                page_size: pageSize,
                sort_by: sortBy,
                filter_by: filterBy,
                search_text: searchText
            },
            request_payload: extraPayload
        }
    };
}
