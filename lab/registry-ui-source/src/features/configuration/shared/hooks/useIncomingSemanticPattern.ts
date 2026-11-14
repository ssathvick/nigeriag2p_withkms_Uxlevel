import { useState } from 'react';
import { useFetch } from '@/shared/hooks';
import { IncomingSemanticPattern } from './useAllSemanticPatterns';
import { useTranslations } from 'next-intl';
import { toast } from 'react-toastify';

export function useIncomingSemanticPattern() {
    const t = useTranslations();
    const [selectedSemanticPattern, setSelectedSemanticPattern] = useState<IncomingSemanticPattern | undefined>(undefined);
    const { execute, loading, error } = useFetch<IncomingSemanticPattern>();

    const fetchSemanticPattern = async (id: string) => {
        try {
            const result = await execute('/api/configuration/ingest/get-semantic-pattern', {
                method: 'POST',
                body: JSON.stringify({ semantic_pattern_id: id })
            });
            if (result) {
                setSelectedSemanticPattern(result);
            }
            return result;
        } catch (error) {
            toast.error(t('toast_operation_failed'));
            return null;
        }
    };

    return {
        selectedSemanticPattern,
        setSelectedSemanticPattern,
        fetchSemanticPattern,
        loading,
        error
    };
}
