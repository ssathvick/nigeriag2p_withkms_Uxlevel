'use client';

import { useState, useCallback } from 'react';
import { useFetch } from '@/shared/hooks/useFetch';
import { Theme, ThemeAttribute, ThemeAttributeUpdate } from '../types';

export function useTheme() {
    const [selectedThemeId, setSelectedThemeId] = useState<string | null>(null);
    const [themeAttributes, setThemeAttributes] = useState<ThemeAttribute[]>([]);

    const { data: themesData, loading: themesLoading, execute: fetchThemes } = useFetch<any>({
        url: '/api/configuration/registry/theme/get-all-themes',
        options: { method: 'POST', body: JSON.stringify({}) },
    });

    const { loading: attributesLoading, execute: fetchAttributes } = useFetch<any>();
    const { loading: creating, execute: executeCreate } = useFetch<any>();
    const { loading: updating, execute: executeUpdate } = useFetch<any>();
    const { loading: removing, execute: executeRemove } = useFetch<any>();

    const themes: Theme[] = Array.isArray(themesData) ? themesData : [];

    const loadAttributes = useCallback(async (themeId: string) => {
        const result = await fetchAttributes('/api/configuration/registry/theme/get-theme-values', {
            method: 'POST',
            body: JSON.stringify({ theme_id: themeId }),
        });

        const attrs: ThemeAttribute[] = Array.isArray(result) ? result : [];
        setThemeAttributes(attrs);
        return attrs;
    }, [fetchAttributes]);

    const selectTheme = useCallback(async (themeId: string) => {
        setSelectedThemeId(themeId);
        await loadAttributes(themeId);
    }, [loadAttributes]);

    const createTheme = useCallback(async (themeMnemonic: string, initialValues: ThemeAttributeUpdate[]) => {
        const result = await executeCreate('/api/configuration/registry/theme/create-theme', {
            method: 'POST',
            body: JSON.stringify({ theme_mnemonic: themeMnemonic, theme_values: initialValues }),
        });
        await fetchThemes();
        return result;
    }, [executeCreate, fetchThemes]);

    const updateThemeColors = useCallback(async (themeId: string, updates: ThemeAttributeUpdate[]) => {
        const result = await executeUpdate('/api/configuration/registry/theme/update-theme-values', {
            method: 'POST',
            body: JSON.stringify({ theme_id: themeId, theme_attribute_values: updates }),
        });
        await loadAttributes(themeId);
        return result;
    }, [executeUpdate, loadAttributes]);

    const removeTheme = useCallback(async (themeId: string) => {
        const result = await executeRemove('/api/configuration/registry/theme/remove-theme', {
            method: 'POST',
            body: JSON.stringify({ theme_id: themeId }),
        });
        setSelectedThemeId(null);
        setThemeAttributes([]);
        await fetchThemes();
        return result;
    }, [executeRemove, fetchThemes]);

    const getAttributeValue = useCallback((key: string): string => {
        return themeAttributes.find(a => a.attribute_name === key)?.attribute_value ?? '';
    }, [themeAttributes]);

    return {
        themes,
        themesLoading,
        selectedThemeId,
        themeAttributes,
        attributesLoading,
        creating,
        updating,
        removing,
        selectTheme,
        createTheme,
        updateThemeColors,
        removeTheme,
        getAttributeValue,
        loadAttributes,
        refreshThemes: fetchThemes,
    };
}
