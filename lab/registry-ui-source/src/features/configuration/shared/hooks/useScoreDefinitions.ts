import { useFetch } from '@/shared/hooks';
import type { ScoreDefinition } from '../types/registers';

export function useScoreDefinitions(
    registerId: string,
    currentPage: number = 1,
    pageSize: number = 10,
) {
    const { data, loading, error, execute } = useFetch<{
        scoreDefinitions: ScoreDefinition[];
        pagination?: {
            number_of_items: number;
            number_of_pages?: number;
        };
    }>({
        url: '/api/configuration/registers/score/get-score-definitions',
        options: {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                page: currentPage,
                pageSize,
            }),
        },
    });

    const scoreDefinitions = [...(data?.scoreDefinitions ?? [])].sort((a, b) =>
        (a.score_type ?? '').localeCompare(b.score_type ?? ''),
    );

    return {
        scoreDefinitions,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
