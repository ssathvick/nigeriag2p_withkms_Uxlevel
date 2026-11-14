import { useFetch } from '@/shared/hooks';
import type { AwePolicyScope } from '@/features/configuration/awe-policy-config/constants';

export interface AwePolicyConfiguration {
    awe_policy_config_id: string;
    policy_scope: AwePolicyScope;
    register_id: string;
    intake_form_id?: string | null;
    section_id?: string | null;
    policy_type: string;
    policy_key: string;
    context_field_names?: string[] | null;
}

export function useAllAwePolicyConfigurations(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        awe_policy_configurations: AwePolicyConfiguration[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/awe-policy-config/all',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize,
            }),
        },
    });

    return {
        awePolicyConfigurations: data?.awe_policy_configurations || [],
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
