import { useFetch } from '@/shared/hooks';

export interface ChangeRequestDocument {
    document_label: string;
    document_store_id: string;
    document_url: string;
}

export function useChangeRequestDocuments(
    changeRequestId?: string,
    enabled = true
) {
    const { data, loading, error } = useFetch<{
        documents: ChangeRequestDocument[];
    }>({
        url: '/api/change-request/get-documents',
        enabled: enabled && !!changeRequestId,
        options: {
            method: 'POST',
            body: JSON.stringify({
                change_request_id: changeRequestId
            })
        },
    });
    return {
        documents: data?.documents ?? [],
        loading,
        error,
    };
}
