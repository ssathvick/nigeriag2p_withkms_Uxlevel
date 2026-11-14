import { portalApi } from "@/shared/utils/apiClient";

export const fetchBanks = (sparUrl: string) =>
    portalApi("/api/dfsp/banks", { sparUrl });

export const fetchWalletProviders = (sparUrl: string) =>
    portalApi("/api/dfsp/wallets", { sparUrl });

export const fetchBranchesByBankId = (
    sparUrl: string,
    bankId: number
) =>
    portalApi("/api/dfsp/branches", { sparUrl, bankId });
