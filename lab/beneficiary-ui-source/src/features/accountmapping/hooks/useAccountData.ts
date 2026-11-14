"use client";

import { useEffect, useState } from "react";
import {
    fetchBanks,
    fetchWalletProviders,
} from "@/features/accountmapping/utils/dfspApi";
import type { Bank, Branch, WalletProvider } from "@/features/accountmapping/types";
import { useSparUrl } from "@/features/accountmapping/hooks";
import { fetchBranchesByBankId } from "../utils/dfspApi";

export function useAccountData() {
    const sparUrl = useSparUrl();

    const [banks, setBanks] = useState<Bank[]>([]);
    const [walletProviders, setWalletProviders] = useState<WalletProvider[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!sparUrl) return;

        async function load() {
            try {
                setLoading(true);

                const [banksRes, walletsRes] = await Promise.all([
                    fetchBanks(sparUrl),
                    fetchWalletProviders(sparUrl),
                ]);

                setBanks(
                    banksRes?.response_body?.response_payload?.banks || []
                );

                setWalletProviders(
                    walletsRes?.response_body?.response_payload
                        ?.wallet_service_providers || []
                );
            } catch (e) {
                setError(e instanceof Error ? e : new Error("DFSP fetch failed"));
            } finally {
                setLoading(false);
            }
        }

        load();
    }, [sparUrl]);

    return { banks, walletProviders, loading, error };
}

export function useBranches(bankName: string, banks: Bank[]) {
    const sparUrl = useSparUrl();
    const [branches, setBranches] = useState<Branch[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!sparUrl) return;

        if (!bankName) {
            setBranches([]);
            return;
        }

        const selectedBank = banks.find((b) => b.bank_name === bankName);
        if (!selectedBank) {
            setBranches([]);
            return;
        }

        setLoading(true);
        fetchBranchesByBankId(sparUrl, selectedBank.id)
            .then((res) => {
                setBranches(
                    res?.response_body?.response_payload?.branches || []
                );
            })
            .catch(() => setBranches([]))
            .finally(() => setLoading(false));
    }, [bankName, banks, sparUrl]);

    return { branches, loading };
}
