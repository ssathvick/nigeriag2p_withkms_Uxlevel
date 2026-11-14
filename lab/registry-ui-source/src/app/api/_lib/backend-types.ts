import "server-only";

export interface RequestHeader {
    sender_app_mnemonic: string;
    sender_app_url: string;
    request_id: string;
    request_timestamp: string;
}

export interface PaginationRequest {
    current_page?: number;
    page_size?: number;
    sort_by?: string;
    search_text?: string;

    filter_by?: {
        [field: string]: {
            // equality
            eq?: string | number | boolean | null;
            neq?: string | number | boolean | null;

            // list based
            in?: Array<string | number>;
            nin?: Array<string | number>;

            // text based
            contains?: string;
            ncontains?: string;
            startsWith?: string;
            endsWith?: string;

            // comparison
            gt?: string | number;
            gte?: string | number;
            lt?: string | number;
            lte?: string | number;

            // null check
            isNull?: boolean;
        };
    };
}


export interface RequestBody {
    pagination_request?: PaginationRequest
    request_payload: any;

}

export interface BackendRequest {
    request_header: RequestHeader;
    request_body: RequestBody;
}

export interface ResponseHeader {
    request_id: string;
    response_status: string;
    response_error_code: string;
    response_error_message: string;
    response_timestamp: string;
}

export interface PaginationResponse {
    current_page?: number;
    page_size?: number;
    number_of_items?: number;
    number_of_pages?: number;
}

export interface ResponseBody<T = any> {
    pagination_response: PaginationResponse | null;
    response_payload: T;
}

export interface BackendResponse<T = any> {
    response_header: ResponseHeader;
    response_body: ResponseBody<T>;
}
