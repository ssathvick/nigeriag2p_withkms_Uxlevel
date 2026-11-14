import { PaginationRequest } from '@/app/api/_lib/backend-types';

/**
 * Extracts pagination request from params
 *
 * @param params - Parameters object that may contain pagination_request or pagination fields
 * @returns PaginationRequest if found, undefined otherwise
 */
export function extractPagination(params: Record<string, any>): PaginationRequest | undefined {
    // Check if pagination_request is directly in params
    if (params.pagination_request && typeof params.pagination_request === 'object') {
        return params.pagination_request as PaginationRequest;
    }

    // Check for individual pagination fields
    const hasPaginationFields =
        params.current_page !== undefined ||
        params.page_size !== undefined ||
        params.sort_by !== undefined ||
        params.search_text !== undefined ||
        params.filter_by !== undefined;

    if (hasPaginationFields) {
        const pagination: PaginationRequest = {};

        if (params.current_page !== undefined) {
            pagination.current_page = params.current_page;
        }
        if (params.page_size !== undefined) {
            pagination.page_size = params.page_size;
        }
        if (params.sort_by !== undefined) {
            pagination.sort_by = params.sort_by;
        }
        if (params.search_text !== undefined) {
            pagination.search_text = params.search_text;
        }
        if (params.filter_by !== undefined) {
            pagination.filter_by = params.filter_by;
        }

        return pagination;
    }

    return undefined;
}

/**
 * Separates pagination from request payload
 *
 * @param params - Combined parameters object
 * @returns Object with pagination and payload separated
 */
export function separatePaginationAndPayload(params: Record<string, any>): {
    pagination?: PaginationRequest;
    payload: Record<string, any>;
} {
    const pagination = extractPagination(params);

    // Remove pagination fields from payload
    const payload = { ...params };
    delete payload.pagination_request;
    delete payload.current_page;
    delete payload.page_size;
    delete payload.sort_by;
    delete payload.search_text;
    delete payload.filter_by;

    return {
        pagination,
        payload,
    };
}
