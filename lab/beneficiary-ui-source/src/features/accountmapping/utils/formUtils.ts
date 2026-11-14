import { STRATEGIES } from "@/features/accountmapping/utils/strategyMap";
import type { Bank, Branch, WalletProvider, FaData, AccountType, WalletType } from "@/features/accountmapping/types";

interface BuildFaDataParams {
    accountType: AccountType;
    walletType: WalletType;
    bank: string;
    banks: Bank[];
    branch: string;
    branches: Branch[];
    accountNumber: string;
    walletProvider: string;
    walletProviders: WalletProvider[];
    mobile: string;
    email: string;
}

export function buildFaData(params: BuildFaDataParams): FaData | undefined {
    const {
        accountType,
        walletType,
        bank,
        banks,
        branch,
        branches,
        accountNumber,
        walletProvider,
        walletProviders,
        mobile,
        email,
    } = params;

    if (accountType === "bank") {
        return {
            strategy_id: STRATEGIES.BANK.id,
            fa_type: STRATEGIES.BANK.type,
            bank_name: bank,
            bank_code: banks.find((b) => b.bank_name === bank)?.bank_code,
            branch_name: branch,
            branch_code: branches.find((br) => br.branch_name === branch)?.branch_code,
            account_number: accountNumber,
        };
    }

    if (accountType === "wallet" && walletType === "Mobile Wallet") {
        return {
            strategy_id: STRATEGIES.MOBILE_WALLET.id,
            fa_type: STRATEGIES.MOBILE_WALLET.type,
            wallet_provider_name: walletProvider,
            wallet_provider_code: walletProviders.find((w) => w.sp_name === walletProvider)?.sp_code,
            mobile_number: mobile,
        };
    }

    if (accountType === "wallet" && walletType === "Email Wallet") {
        return {
            strategy_id: STRATEGIES.EMAIL_WALLET.id,
            fa_type: STRATEGIES.EMAIL_WALLET.type,
            wallet_provider_name: walletProvider,
            wallet_provider_code: walletProviders.find((w) => w.sp_name === walletProvider)?.sp_code,
            email_address: email,
        };
    }
}
