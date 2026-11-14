"use client";

import { useState } from "react";
import { linkAccountApi } from "../utils/accountApi";
import { useSparUrl } from "./useSparUrl";

export function useLinkAccount() {
    const sparUrl = useSparUrl();
    const [linking, setLinking] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    async function handleLink( faData: any) {
        try {
            setLinking(true);
            setError(null);
            setResult(null);

            const linkRequest = [
                {
                    reference_id: "ref-" + Date.now(),
                    timestamp: new Date().toISOString(),
                    id: "",
                    fa: faData,
                    name: "",
                    phone_number: "",
                    additional_info: [],
                    locale: "en",
                },
            ];

            const response = await linkAccountApi(
                sparUrl,
                "txn-" + Date.now(),
                linkRequest
            );

            const status =
                response?.response_body?.response_payload?.link_response?.[0]?.status;

            setResult(status);
            return response;
        } catch (err: any) {
            setError(err.message || "Failed to link account");
            throw err;
        } finally {
            setLinking(false);
        }
    }

    return { handleLink, linking, result, error };
}
