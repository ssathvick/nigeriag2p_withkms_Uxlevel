'use client';
import '@/components/shared/NigeriaGeographyWidget';
import '@/components/shared/HouseholdMembersWidget';
import '@/components/shared/HouseholdLookupWidget';

import React, {
    createContext,
    useContext,
    useMemo,
} from 'react';
import { useParams } from 'next/navigation';
import { useFetch } from '@/shared/hooks/useFetch';

export interface Register {
    register_id: string;
    register_mnemonic: string;
    register_subject: string;
    register_description: string;
    master_register_id: string | null;
}

interface RegisterContextValue {
    registers: Register[];
    currentRegister?: Register;
    loading: boolean;
}

export const RegisterContext = createContext<RegisterContextValue | null>(null);

export function RegisterProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    const params = useParams<{ type?: string }>();


    const { data, loading } = useFetch<Register[]>({
        url: '/api/register/all',
    });
    const registers = data ?? [];

    const currentRegister = useMemo(() => {
        if (!params?.type) return undefined;

        return registers.find(
            r =>
                r.register_mnemonic.toLowerCase() ===
                params.type!.toLowerCase()
        );
    }, [params?.type, registers]);

    const value = useMemo(
        () => ({
            registers,
            currentRegister,
            loading,
        }),
        [registers, currentRegister, loading]
    );

    return (
        <RegisterContext.Provider value={value}>
            {children}
        </RegisterContext.Provider>
    );
}

export function useRegister() {
    const ctx = useContext(RegisterContext);
    if (!ctx) {
        throw new Error(
            'useRegister must be used inside RegisterProvider'
        );
    }
    return ctx;
}
