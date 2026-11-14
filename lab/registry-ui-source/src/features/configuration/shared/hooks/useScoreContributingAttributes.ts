import { useFetch } from '@/shared/hooks';
import type { ScoreContributingAttribute } from '../types/registers';

export function useScoreContributingAttributes(
    scoreDefinitionId: string,
    page: number = 1,
    pageSize: number = 10,
) {
    const { data, loading, error, execute } = useFetch<{
        contributingAttributes: ScoreContributingAttribute[];
        pagination?: {
            number_of_items: number;
            number_of_pages?: number;
        };
    }>({
        url: '/api/configuration/registers/score/attribute/get-score-contributing-attributes',
        options: {
            method: 'POST',
            body: JSON.stringify({
                score_definition_id: scoreDefinitionId,
                page,
                pageSize,
            }),
        },
    });

    const contributingAttributes = [
        ...(data?.contributingAttributes ?? []),
    ].sort((a, b) =>
        (a.attribute_name ?? '').localeCompare(b.attribute_name ?? ''),
    );

    return {
        contributingAttributes,
        pagination: data?.pagination,
        loading,
        error,
        refresh: execute,
    };
}
