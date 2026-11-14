'use client';

import { useCallback, useState, useEffect } from 'react';
import { useFetch } from '@/shared/hooks/useFetch';
import { Language } from '../types';

export function useLang() {
    const [languages, setLanguages] = useState<Language[]>([]);

    const { data: languagesData, loading: languagesLoading, execute: fetchLanguages } = useFetch<Language[]>({
        url: '/api/configuration/registry/language/get-all-languages',
        options: { method: 'POST', body: JSON.stringify({}) },
    });

    const { loading: languageLoading, execute: fetchLanguage } = useFetch<any>();
    const { loading: creating, execute: executeCreate } = useFetch<any>();
    const { loading: updating, execute: executeUpdate } = useFetch<any>();
    const { loading: removing, execute: executeRemove } = useFetch<any>();

    useEffect(() => {
        if (Array.isArray(languagesData)) {
            setLanguages(languagesData);
        }
    }, [languagesData]);

    const getLanguage = useCallback(async (languageId: string) => {
        return await fetchLanguage('/api/configuration/registry/language/get-language', {
            method: 'POST',
            body: JSON.stringify({ language_id: languageId }),
        });
    }, [fetchLanguage]);

    const createLanguage = useCallback(async (language: Omit<Language, 'language_id'>) => {
        const result = await executeCreate('/api/configuration/registry/language/create-language', {
            method: 'POST',
            body: JSON.stringify(language),
        });
        if (result) {
            await fetchLanguages();
        }
        return result;
    }, [executeCreate, fetchLanguages]);

    const updateLanguage = useCallback(async (language: Language) => {
        const result = await executeUpdate('/api/configuration/registry/language/update-language', {
            method: 'POST',
            body: JSON.stringify(language),
        });
        if (result) {
            await fetchLanguages();
        }
        return result;
    }, [executeUpdate, fetchLanguages]);

    const removeLanguage = useCallback(async (languageId: string) => {
        const result = await executeRemove('/api/configuration/registry/language/remove-language', {
            method: 'POST',
            body: JSON.stringify({ language_id: languageId }),
        });
        if (result) {
            await fetchLanguages();
        }
        return result;
    }, [executeRemove, fetchLanguages]);

    return {
        languages,
        setLanguages,
        languagesLoading,
        languageLoading,
        creating,
        updating,
        removing,
        fetchLanguages,
        getLanguage,
        createLanguage,
        updateLanguage,
        removeLanguage,
    };
}
