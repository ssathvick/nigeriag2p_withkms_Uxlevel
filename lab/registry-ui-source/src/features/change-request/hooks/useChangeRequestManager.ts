import { useState, useEffect, useCallback, useMemo } from "react";
import { toast } from "react-toastify";
import { useFetch } from "@/shared/hooks/useFetch";
import type { ChangeRequest } from "@/features/change-request/types/change-request";
import { ChangeRequestDocument } from "../components/ChangeRequestHeader";
import { useTranslations } from "next-intl";

type PopupType = "approve" | "reject-input" | "reject" | null;

export function useChangeRequestManager(changeId: string) {
    const t = useTranslations();
    const [details, setDetails] = useState<ChangeRequest | null>(null);
    const [documents, setDocuments] = useState<ChangeRequestDocument[]>([]);

    const [loadingDetails, setLoadingDetails] = useState(true);
    const [loadingDocuments, setLoadingDocuments] = useState(true);
    const [loadingAction, setLoadingAction] = useState(false);

    const [popupVisible, setPopupVisible] = useState(false);
    const [popupType, setPopupType] = useState<PopupType>(null);

    const detailsFetchOptions = useMemo(
        () => ({
            method: "POST" as const,
            body: JSON.stringify({ change_request_id: changeId }),
        }),
        [changeId],
    );

    const { data: detailsData, loading: detailsLoading, execute: fetchDetails } =
        useFetch<ChangeRequest>({
            url: "/api/change-request/get",
            enabled: !!changeId,
            options: detailsFetchOptions,
        });

    const { data: documentsData, loading: documentsLoading } = useFetch<{ documents: ChangeRequestDocument[] }>({
        url: "/api/change-request/get-documents",
        enabled: !!changeId,
        options: {
            method: "POST",
            body: JSON.stringify({ change_request_id: changeId }),
        },
    });

    const { execute: executeApprove } = useFetch();
    const { execute: executeReject } = useFetch();

    useEffect(() => {
        if (detailsData) setDetails(detailsData);
        setLoadingDetails(detailsLoading);
    }, [detailsData, detailsLoading]);

    useEffect(() => {
        if (documentsData?.documents) setDocuments(documentsData.documents);
        setLoadingDocuments(documentsLoading)
    }, [documentsData]);

    const refetchDetails = useCallback(async () => {
        const result = (await fetchDetails("/api/change-request/get", detailsFetchOptions)) as
            | ChangeRequest
            | { error?: string }
            | null;
        if (result && typeof result === "object" && !("error" in result && result.error)) {
            setDetails(result as ChangeRequest);
        }
    }, [changeId, fetchDetails, detailsFetchOptions]);

    const handleApprove = useCallback(async () => {
        setLoadingAction(true);
        try {
            const endpoint = (details as ChangeRequest)?.is_core_section ? "/api/change-request/core-section/approve" : "/api/change-request/approve";
            const res = await executeApprove(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ change_request_id: changeId }),
            });

            if ("error" in res && res.error) {
                toast.error(t('toast_operation_error', { error: res.error }), {
                    position: "top-right",
                    autoClose: 5000,
                });
                return;
            }
            if (res.approval_status === "APPROVED") {
                toast.success(t('toast_cr_approved'), {
                    position: "top-right",
                    autoClose: 4000,
                });

                setDetails(prev => {
                    if (!prev) return prev;
                    return { ...prev, approval_status: "APPROVED" };
                });
            }
        } catch {
            toast.error(t('toast_cr_approve_failed'), {
                autoClose: 5000,
            });
        } finally {
            setLoadingAction(false);
        }
    }, [changeId, executeApprove, details]);

    const handleRejectClick = useCallback(() => {
        setPopupType("reject-input");
        setPopupVisible(true);
    }, []);

    const submitReject = useCallback(
        async (reason: string) => {
            setLoadingAction(true);
            try {
                const endpoint = (details as ChangeRequest)?.is_core_section ? "/api/change-request/core-section/reject" : "/api/change-request/reject";
                const res = await executeReject(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ change_request_id: changeId, rejection_reason: reason }),
                });

                if (res) {
                    setPopupVisible(false);

                    toast.success(t('toast_cr_rejected'), {
                        position: "top-right",
                        autoClose: 4000,
                    });

                    setDetails((prev) => {
                        if (!prev) return prev;
                        return { ...prev, approval_status: "REJECTED" };
                    });
                }
            } catch {
                toast.error(t('toast_cr_reject_failed'), {
                    autoClose: 5000,
                });
            } finally {
                setLoadingAction(false);
            }
        },
        [changeId, executeReject, details]
    );

    return {
        details,
        documents,
        loadingDetails,
        loadingDocuments,
        loadingAction,
        popupVisible,
        popupType,
        setPopupVisible,
        handleApprove,
        handleReject: handleRejectClick,
        submitReject,
        refetchDetails,
    };
}
