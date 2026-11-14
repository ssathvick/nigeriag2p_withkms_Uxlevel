import { useState } from 'react';
import { useFetch } from '@/shared/hooks';
import { IncomingKeyPath } from './useAllIncomingKeyPaths';

export function useIncomingKeyPath() {
    const [selectedKeyPath, setSelectedKeyPath] = useState<IncomingKeyPath | undefined>(undefined);
    const { execute, loading, error } = useFetch<IncomingKeyPath>();

    const fetchKeyPath = async (keyPathId: string) => {
        const result = await execute('/api/configuration/ingest/get-key-path', {
            method: 'POST',
            body: JSON.stringify({ key_path_id: keyPathId })
        });
        if (result) {
            setSelectedKeyPath(result);
        }
        return result;
    };

    return {
        selectedKeyPath,
        setSelectedKeyPath,
        fetchKeyPath,
        loading,
        error
    };
}
