"use client";

import { routeServiceEndpoint } from '@/shared/utils/serviceRouteMapper';
import { separatePaginationAndPayload } from '@/shared/utils/paginationHelper';

/**
 * Type definition for DataSourceRequestHandler
 * Matches the widget library's expected signature
 */
export type DataSourceRequestHandler = (
    service: string,
    endpoint: string,
    method: string,
    params: Record<string, any>,
    options?: { headers?: Record<string, string> }
) => Promise<any>;

/**
 * Internal implementation of the data source request handler
 */
const _dataSourceRequestHandler: DataSourceRequestHandler = async (
    service: string,
    endpoint: string,
    method: string,
    params: Record<string, any>,
    options?: { headers?: Record<string, string> }
) => {
    try {
        // Route service + endpoint to actual Next.js API URL
        const url = routeServiceEndpoint(service, endpoint);

        // Separate pagination from request payload
        const { pagination, payload } = separatePaginationAndPayload(params);

        // Build request body
        const requestBody: any = {
            ...payload,
        };

        // Add pagination if present
        if (pagination) {
            requestBody.pagination_request = pagination;
        }

        // Make API call to Next.js route
        const response = await fetch(url, {
            method: method || 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...options?.headers,
            },
            body: JSON.stringify(requestBody),
        });

        // Handle HTTP errors
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                errorData.error || errorData.message || `API error: ${response.statusText}`
            );
        }

        // Parse response
        const data = await response.json();

        // Handle OpenG2P error responses (if response comes in OpenG2P format)
        if (data.response_header?.response_status === 'ERROR') {
            throw new Error(
                data.response_header.response_error_message || 'Backend error occurred'
            );
        }

        // Extract response payload if in OpenG2P format, otherwise return as-is
        if (data.response_body?.response_payload !== undefined) {
            return data.response_body.response_payload;
        }

        // Return data as-is if not in OpenG2P format (Next.js API routes already extract it)
        return data;
    } catch (error) {
        console.error('DataSourceRequestHandler error:', error);
        throw error;
    }
};

/**
 * Adapter function that handles both old and new widget library signatures
 *
 * Old signature (for backward compatibility): apiAdapter(url, options)
 * New signature: dataSourceRequestHandler(service, endpoint, method, params, options)
 *
 * This function detects which signature is being used and routes accordingly.
 */
export const dataSourceRequestHandler: any = async (
    arg1: string,
    arg2?: string | any,
    arg3?: string | any,
    arg4?: Record<string, any> | any,
    arg5?: { headers?: Record<string, string> } | any
) => {
    // Detect if this is the new signature (service, endpoint, method, params, options)
    // New signature: arg1=service (string), arg2=endpoint (string), arg3=method (string)
    // Old signature: arg1=url (string), arg2=options (object with method, headers, body)

    if (typeof arg2 === 'string' && typeof arg3 === 'string') {
        // New signature: (service, endpoint, method, params, options)
        return _dataSourceRequestHandler(
            arg1 as string,      // service
            arg2 as string,      // endpoint
            arg3 as string,      // method
            arg4 as Record<string, any> || {}, // params
            arg5 as { headers?: Record<string, string> } // options
        );
    } else {
        // Old signature: (url, options)
        // This is for backward compatibility with widgets that haven't been updated yet
        const url = arg1 as string;
        const options = arg2 as any || {};

        // Extract service and endpoint from URL pattern: /api/{service}/{endpoint}
        const urlMatch = url.match(/^\/api\/([^/]+)\/(.+)$/);
        if (!urlMatch) {
            throw new Error(`Invalid API URL format: ${url}. Expected format: /api/{service}/{endpoint}`);
        }

        const [, service, endpoint] = urlMatch;

        // Parse body if it's a string
        let params: Record<string, any> = {};
        if (options.body) {
            if (typeof options.body === 'string') {
                try {
                    params = JSON.parse(options.body);
                } catch (e) {
                    params = {};
                }
            } else {
                params = options.body;
            }
        }

        return _dataSourceRequestHandler(
            service,
            endpoint,
            options.method || 'POST',
            params,
            { headers: options.headers }
        );
    }
};
