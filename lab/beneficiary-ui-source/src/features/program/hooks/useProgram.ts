"use client";
import { useEffect, useState } from "react";
import { getProgramById } from "@/features/program/utils/programsApi"
import { usePbmsUrl } from "@/features/program/hooks";


export function useProgram(programId: string) {
    const pbmsUrl = usePbmsUrl();

    const [program, setProgram] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!programId || !pbmsUrl) return;
        async function fetchProgram(baseUrl: string) {
            setLoading(true);
            const result = await getProgramById(baseUrl, programId);
            setProgram(result?.response_body?.response_payload ?? null);
            setLoading(false);
        };

        fetchProgram(pbmsUrl);
    }, [programId, pbmsUrl]);

    return { program, loading };
}
