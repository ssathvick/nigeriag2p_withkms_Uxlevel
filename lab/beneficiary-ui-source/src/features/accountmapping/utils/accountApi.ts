import { portalApi } from "@/shared/utils/apiClient";

export const resolveAccountApi = (
    sparUrl: string,
    transactionId: string,
    resolveRequest: any[]
) =>
    portalApi("/api/account-mapper/resolve", {
        sparUrl,
        transactionId,
        resolveRequest,
    });

export const linkAccountApi = (
    sparUrl: string,
    transactionId: string,
    linkRequest: any[]
) =>
    portalApi("/api/account-mapper/link", {
        sparUrl,
        transactionId,
        linkRequest,
    });

export const unlinkAccountApi = (
    sparUrl: string,
    transactionId: string,
    unlinkRequest: any[]
) =>
    portalApi("/api/account-mapper/unlink", {
        sparUrl,
        transactionId,
        unlinkRequest,
    });

export const updateAccountApi = (
    sparUrl: string,
    transactionId: string,
    updateRequest: any[]
) =>
    portalApi("/api/account-mapper/update", {
        sparUrl,
        transactionId,
        updateRequest,
    });
