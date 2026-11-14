import { useFetch } from '@/shared/hooks';

export interface DataPolicy {
    policy_id: string;
    policy_mnemonic: string;
    policy_description: string;
    register_id: string;
    policy_type: string;
    policy_filter_expression: Record<string, unknown>;
}

export function usePolicies(
    registerId: string,
    currentPage: number = 1,
    pageSize: number = 10,
) {
    const { data, loading, error, execute } = useFetch<{
        policies: DataPolicy[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/data-policy/get-policies',
        enabled: !!registerId,
        options: {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                current_page: currentPage,
                page_size: pageSize,
            }),
        },
    });

    return {
        policies: data?.policies || [],
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
