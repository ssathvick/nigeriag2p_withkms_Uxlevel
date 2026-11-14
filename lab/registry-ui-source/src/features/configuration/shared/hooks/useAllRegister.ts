import { useMemo } from 'react';
import { useFetch } from '@/shared/hooks';
import { Register } from '../types';

export function useAllRegister(page?: number, pageSize?: number) {
    const { data, loading, error, execute } = useFetch<{
        registers: Register[];
        pagination?: {
            number_of_items: number;
            number_of_pages: number;
        };
    }>({
        url: '/api/configuration/registers/all',
        options: {
            method: 'POST',
            body: JSON.stringify({
                current_page: page,
                page_size: pageSize
            })
        }
    });

    // Ascending order
    const registers = (data?.registers || [])
        .sort((a, b) => (a.register_rank ?? 0) - (b.register_rank ?? 0));

    return {
        registers,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
