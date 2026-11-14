export interface Bank {
  id: number;
  bank_name: string;
  bank_code: string;
}

export interface Branch {
  branch_name: string;
  branch_code: string;
}

export interface WalletProvider {
  sp_name: string;
  sp_code: string;
  wallet_type: string;
}

export interface FaData {
  strategy_id: number;
  fa_type: string;
  bank_name?: string;
  bank_code?: string;
  branch_name?: string;
  branch_code?: string;
  account_number?: string;
  wallet_provider_name?: string;
  wallet_provider_code?: string;
  mobile_number?: string;
  email_address?: string;
}

export type AccountType = "bank" | "wallet";
export type WalletType = "Mobile Wallet" | "Email Wallet";
