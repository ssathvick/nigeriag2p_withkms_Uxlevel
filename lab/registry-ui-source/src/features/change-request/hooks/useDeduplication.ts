import { useFetch } from "@/shared/hooks/useFetch";

export function useDeduplication(changeRequestId: string, type: "change-request" | "register") {
    const { data, loading } = useFetch({
        enabled: !!changeRequestId,
        url: `/api/change-request/deduplication/${type}`,
        options: {
            method: 'POST',
            body: JSON.stringify({
                change_request_id: changeRequestId,
                current_page: 1,
                page_size: 20,
            }),
        }

    });

    return {
        results: data?.results || [],
        loading
    };
}
