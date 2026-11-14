'use client';

import { useFetch } from '@/shared/hooks';

interface RegisterSchema {
    register_id: string;
    deduplicate_schema: any[];
    search_result_schema: any[];
    filter_schema: any[];
}

export const useRegisterSchema = (
    registerId: string
) => {

    const { data, loading, execute } = useFetch<RegisterSchema>({
        url: '/api/configuration/registers/register-schema',
        options: {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
            }),
        },
    });
    return {
        schema: data,
        loading,
        refresh: execute
    };
};
