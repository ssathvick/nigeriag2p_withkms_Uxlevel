'use client';

import {
    createContext,
    useContext,
    useEffect,
    useMemo,
    useState,
    useCallback,
    ReactNode,
} from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks';
import { TabConfig } from '@/shared/types';
import { usePathname, useRouter } from '@/i18n/navigation';
import { useRegister } from './RegisterContext';


/* ------------------------------------------------------------------ */
/* Context types */
/* ------------------------------------------------------------------ */

interface RegisterTabsContextValue {
    tabs: TabConfig[];
    activeTabIndex: number;
    activeTab?: TabConfig;
    activeTabId?: string;
    setActiveTabByIndex: (index: number) => void;
    setActiveTabById: (tabId: string) => void;
}

/* ------------------------------------------------------------------ */

export const RegisterTabsContext =
    createContext<RegisterTabsContextValue | null>(null);

/* ------------------------------------------------------------------ */
/* Provider */
/* ------------------------------------------------------------------ */

export function RegisterTabsProvider({ children }: { children: ReactNode }) {
    const { id } = useParams<{ type: string; id?: string }>();
    const searchParams = useSearchParams();
    const router = useRouter();
    const pathname = usePathname();


    const tabFromUrl = searchParams.get('tab');
    const { currentRegister } = useRegister();

    const fetchOptions = useMemo(() => ({
        method: 'POST',
        body: JSON.stringify({
            register_id: currentRegister?.register_id,
        }),
    }), [currentRegister?.register_id]);

    const { data } = useFetch<TabConfig[]>({
        url: `/api/register/get-all-tabs`,
        options: fetchOptions,
        enabled: !!currentRegister?.register_id,
    });

    const tabs = data ?? [];

    const [activeTabIndex, setActiveTabIndex] = useState(0);

    useEffect(() => {
        if (!tabs.length || !tabFromUrl) return;

        const index = tabs.findIndex(tab => tab.tab_id === tabFromUrl);
        if (index >= 0) {
            setActiveTabIndex(index);
        }
    }, [tabs, tabFromUrl]);


    const activeTab = tabs[activeTabIndex];
    const activeTabId = activeTab?.tab_id;

    const updateUrl = useCallback(
        (tabId: string, replace = false) => {
            if (!id) return;

            const params = new URLSearchParams(searchParams.toString());
            params.set('tab', tabId);
            const search = params.toString();
            const url = `${pathname}?${search}`;

            if (replace) {
                router.replace(url);
            } else {
                router.push(url);
            }
        },
        [router, pathname, id, searchParams]
    );

    // Handle initial redirect to default tab if none specified in URL
    useEffect(() => {
        if (!tabs.length) return;

        if (tabFromUrl) return;

        setActiveTabIndex(0);
        updateUrl(tabs[0].tab_id, true);
    }, [tabs, tabFromUrl, updateUrl]);


    const setActiveTabByIndex = useCallback(
        (index: number) => {
            const tab = tabs[index];
            if (!tab) return;

            setActiveTabIndex(index);
            updateUrl(tab.tab_id);
        },
        [tabs, updateUrl]
    );

    const setActiveTabById = useCallback(
        (tabId: string) => {
            const index = tabs.findIndex(tab => tab.tab_id === tabId);
            if (index < 0) return;

            setActiveTabIndex(index);
            updateUrl(tabId);
        },
        [tabs, updateUrl]
    );


    const value = useMemo(
        () => ({
            tabs,
            activeTabIndex,
            activeTab,
            activeTabId,
            setActiveTabByIndex,
            setActiveTabById,
        }),
        [
            tabs,
            activeTabIndex,
            activeTab,
            activeTabId,
            setActiveTabByIndex,
            setActiveTabById,
        ]
    );

    return (
        <RegisterTabsContext.Provider value={value}>
            {children}
        </RegisterTabsContext.Provider>
    );
}

export function useRegisterTabs(): RegisterTabsContextValue {
    const ctx = useContext(RegisterTabsContext);

    if (!ctx) {
        throw new Error(
            'useRegisterTabs must be used inside RegisterTabsProvider'
        );
    }

    return ctx;
}
