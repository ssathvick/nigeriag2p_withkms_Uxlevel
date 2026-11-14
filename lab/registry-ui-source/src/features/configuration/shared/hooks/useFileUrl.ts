'use client';

import { useFetch } from '@/shared/hooks';
import { useState } from 'react';

interface FileUrlResponse {
    file_url: string;
}

export function useFileUrl() {
    const { execute, loading, error } = useFetch<FileUrlResponse>();
    const [fileUrl, setFileUrl] = useState<string | null>(null);

    const getFileUrl = async (documentStoreId: string) => {
        if (!documentStoreId) return null;

        const result = await execute(
            '/api/configuration/data-models/template-get',
            {
                method: 'POST',
                body: JSON.stringify({
                    document_store_id: documentStoreId,
                }),
            }
        );
        const url = result?.file_url ?? null;
        setFileUrl(url);

        return url;
    };

    return {
        fileUrl,
        getFileUrl,
        loading,
        error,
        setFileUrl,
    };
}
