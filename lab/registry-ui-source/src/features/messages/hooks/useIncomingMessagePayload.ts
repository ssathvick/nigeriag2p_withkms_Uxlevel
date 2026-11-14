'use client';

import { useState, useCallback } from 'react';
import { useFetch } from '@/shared/hooks';

export function useIncomingMessagePayload() {
    const [ingestId, setIngestId] = useState<string | null>(null);

    const { data: rawData, loading: rawDataLoading } = useFetch<any>({
        url: '/api/incoming-message/get/raw',
        enabled: !!ingestId,
        options: {
            method: 'POST',
            body: JSON.stringify({ ingest_id: ingestId }),
        },
    });

    const { data: transformedData, loading: transformedDataLoading } = useFetch<any>({
        url: '/api/incoming-message/get/transformed',
        enabled: !!ingestId,
        options: {
            method: 'POST',
            body: JSON.stringify({ ingest_id: ingestId }),
        },
    });

    const fetchAll = useCallback((id: string) => {
        setIngestId(id);
    }, []);

    return {
        fetchAll,
        loading: rawDataLoading || transformedDataLoading,
        rawJson: rawData?.raw_data_json ?? null,
        enrichedJson: transformedData?.enriched_data_json ?? null,
        transformedJson: transformedData?.transformed_data_json ?? null,
    };
}
