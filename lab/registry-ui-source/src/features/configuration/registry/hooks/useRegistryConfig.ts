'use client';

import { useState, useCallback, useEffect } from 'react';
import { useFetch } from '@/shared/hooks/useFetch';

interface RegistryConfig {
    configuration_id: string;
    registry_name: string;
    registry_logo: string;
    registry_theme_id: string;
}

export const useRegistryConfig = () => {
    const [config, setConfig] = useState<RegistryConfig | null>(null);
    const { data: fetchedData, loading: fetchLoading, execute: fetchExecute } = useFetch({ url: '/api/configuration/registry/get' });
    const { loading: updateLoading, execute: updateExecute } = useFetch();

    const fetchConfig = useCallback(async () => {
        const result = await fetchExecute();
        if (result) {
            setConfig(result);
        }
    }, [fetchExecute]);

    useEffect(() => {
        fetchConfig();
    }, [fetchConfig]);

    const updateRegistryTheme = async (themeId: string) => {
        if (!config) return null;

        const payload = {
            configuration_id: config.configuration_id,
            registry_name: config.registry_name,
            registry_logo: config.registry_logo,
            registry_theme_id: themeId,
        };

        const result = await updateExecute('/api/configuration/registry/update', {
            method: 'POST',
            body: JSON.stringify(payload),
        });

        if (result) {
            setConfig(prev => prev ? { ...prev, registry_theme_id: themeId } : null);
            return result;
        }
        return null;
    };

    return {
        config,
        loading: fetchLoading || updateLoading,
        fetchConfig,
        updateRegistryTheme,
        activeThemeId: config?.registry_theme_id || null,
    };
};
