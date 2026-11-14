import { TextInput, SelectInput } from "@/features/accountmapping/components";
import type { AccountType, WalletType, Bank, Branch, WalletProvider } from "@/features/accountmapping/types";

interface AccountFormSectionProps {
    accountType: AccountType;
    setAccountType: (type: AccountType) => void;
    bank: string;
    setBank: (bank: string) => void;
    branch: string;
    setBranch: (branch: string) => void;
    accountNumber: string;
    setAccountNumber: (number: string) => void;
    walletType: WalletType;
    setWalletType: (type: WalletType) => void;
    walletProvider: string;
    setWalletProvider: (provider: string) => void;
    mobile: string;
    setMobile: (mobile: string) => void;
    email: string;
    setEmail: (email: string) => void;
    banks: Bank[];
    branches: Branch[];
    walletProviders: WalletProvider[];
}

export function AccountFormSection({
    accountType,
    setAccountType,
    bank,
    setBank,
    branch,
    setBranch,
    accountNumber,
    setAccountNumber,
    walletType,
    setWalletType,
    walletProvider,
    setWalletProvider,
    mobile,
    setMobile,
    email,
    setEmail,
    banks,
    branches,
    walletProviders,
}: AccountFormSectionProps) {
    return (
        <>
            <div>
                <label className="block text-[16px] text-black font-[500] mb-1">
                    Select Account Type
                </label>
                <select
                    value={accountType}
                    onChange={(e) => setAccountType(e.target.value as AccountType)}
                    className="w-1/2 bg-gray-100 rounded-lg px-3 py-2 text-[16px] font-[500] text-black focus:outline-none"
                >
                    <option value="bank">Bank</option>
                    <option value="wallet">Wallet</option>
                </select>
            </div>

            {accountType === "bank" && (
                <>
                    <SelectInput
                        label="Bank Name"
                        value={bank}
                        options={banks.map((b) => b.bank_name)}
                        onChange={setBank}
                    />
                    <SelectInput
                        label="Branch"
                        value={branch}
                        options={branches.map((br) => br.branch_name)}
                        onChange={setBranch}
                    />
                    <TextInput
                        label="Account Number"
                        value={accountNumber}
                        onChange={setAccountNumber}
                    />
                </>
            )}

            {accountType === "wallet" && (
                <>
                    <SelectInput
                        label="Wallet Type"
                        value={walletType}
                        options={[...new Set(walletProviders.map((w) => w.wallet_type))]}
                        onChange={(val) => setWalletType(val as WalletType)}
                    />

                    <SelectInput
                        label="Wallet Provider"
                        value={walletProvider}
                        options={walletProviders
                            .filter((w) => w.wallet_type === walletType)
                            .map((w) => w.sp_name)}
                        onChange={setWalletProvider}
                    />

                    {walletType === "Mobile Wallet" ? (
                        <TextInput label="Mobile Number" value={mobile} onChange={setMobile} />
                    ) : (
                        <TextInput label="Email Address" type="email" value={email} onChange={setEmail} />
                    )}
                </>
            )}
        </>
    );
}
