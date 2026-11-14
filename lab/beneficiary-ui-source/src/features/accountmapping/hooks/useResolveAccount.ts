"use client";

import { useEffect, useState } from "react";
import { extractResolvedData } from "@/features/accountmapping/utils";
import { useSparUrl } from "@/features/accountmapping/hooks";
import { resolveAccountApi } from "../utils/accountApi";

export function useResolveAccount() {
    const sparUrl = useSparUrl();

    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function handleResolve() {
        try {
            setLoading(true);
            setError(null);

            const resolveRequest = [
                {
                    reference_id: "ref-" + Date.now(),
                    timestamp: new Date().toISOString(),
                    fa: "",
                    id: "",
                    name: "",
                    scope: "details",
                    additional_info: [],
                    locale: "en",
                },
            ];

            const response = await resolveAccountApi(
                sparUrl,
                "txn-" + Date.now(),
                resolveRequest
            );

            setResult(extractResolvedData(response));
        } catch (err: any) {
            setError(err.message || "Failed to resolve account");
            setResult(null);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (sparUrl) handleResolve();
    }, [sparUrl]);

    return { result, loading, error, handleResolve };
}
