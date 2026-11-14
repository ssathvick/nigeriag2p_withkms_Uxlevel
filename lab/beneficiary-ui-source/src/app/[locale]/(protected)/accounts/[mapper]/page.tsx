"use client";

import Image from "next/image";
import { useLocale } from "next-intl";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { prefixBasePath } from "@/shared/utils/path";
import { AuthUtil } from "@/features/auth/components";
import { useAuth } from "@/context/GlobalContext";

import {
    AccountSuccessModal,
    AccountErrorModal,
    AccountRemoveModal,
    AccountFormSection,
    InfoSidebar
} from "@/features/accountmapping/components";

import {
    useUpdateAccount,
    useLinkAccount,
    useAccountData,
    useBranches,
} from "@/features/accountmapping/hooks";


import { buildFaData, getAccountInformation } from "@/features/accountmapping/utils";
import type { AccountType, WalletType } from "@/features/accountmapping/types";

export default function AccountUpdatePage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });
    const { profile } = useAuth();

    const params = useParams();
    const mapper = params.mapper;

    const profileImage = profile?.picture || prefixBasePath("/user_image.png");
    const profileName = profile?.name || "User"

    const [accountType, setAccountType] = useState<AccountType>("bank");
    const [bank, setBank] = useState("");
    const [branch, setBranch] = useState("");
    const [accountNumber, setAccountNumber] = useState("");
    const [mobile, setMobile] = useState(profile?.phone_number || "");
    const [email, setEmail] = useState(profile?.email || "");
    const [walletProvider, setWalletProvider] = useState("");
    const [walletType, setWalletType] = useState<WalletType>("Mobile Wallet");

    const [showModal, setShowModal] = useState(false);
    const [showErrorModal, setShowErrorModal] = useState(false);
    const [showRemoveModal, setShowRemoveModal] = useState(false);
    const [accountInfo, setAccountInfo] = useState<any>(null);

    useEffect(() => {
        getAccountInformation()
            .then((data) => setAccountInfo(data))
            .catch(console.error);
    }, []);

    const { banks, walletProviders } = useAccountData();
    const { branches } = useBranches(bank, banks);

    const { handleLink, linking, result: linkResult, error: linkError } = useLinkAccount();
    const { handleUpdate, updating, result: updateResult, error: updateError } = useUpdateAccount();

    useEffect(() => {
        setBranch("");
    }, [bank]);

    useEffect(() => {
        setWalletProvider("");
    }, [walletType]);

    useEffect(() => {
        if (updateResult === "succ" || linkResult === "succ") {
            setShowModal(true);
        } else if (updateError || linkError) {
            setShowErrorModal(true);
        }
        else if (updateResult === "rjct") {
            setShowErrorModal(true)
        }
    }, [updateResult, linkResult, updateError, linkError]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const faData = buildFaData({
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
        });

        if (mapper === "link") {
            await handleLink(faData);
        } else {
            await handleUpdate(faData);
        }
    };

    return (
        <div className="relative px-[50px] py-4 bg-white min-h-screen">
            <h1 className="text-[18px] font-[600] text-gray-800 mb-4">Update Account</h1>
            <div className="flex flex-row gap-0 rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] overflow-hidden">
                <div className="w-[70%] bg-white p-8">
                    <h2 className="text-[20px] font-[600] text-[#ED7C22] mb-6">
                        Edit Account Information
                    </h2>

                    <form onSubmit={handleSubmit} className="flex flex-row gap-10 items-start">
                        <Image
                            src={profileImage}
                            alt="Profile"
                            width={40}
                            height={40}
                            className="object-cover rounded-full"
                        />

                        <div className="flex flex-col justify-start w-full space-y-4">
                            <div>
                                <div className="text-[16px] font-[500] text-black">Name</div>
                                <div className="text-[20px] text-[#3399FF] font-[500]">
                                    {profileName}
                                </div>
                            </div>

                            <AccountFormSection
                                accountType={accountType}
                                setAccountType={setAccountType}
                                bank={bank}
                                setBank={setBank}
                                branch={branch}
                                setBranch={setBranch}
                                accountNumber={accountNumber}
                                setAccountNumber={setAccountNumber}
                                walletType={walletType}
                                setWalletType={setWalletType}
                                walletProvider={walletProvider}
                                setWalletProvider={setWalletProvider}
                                mobile={mobile}
                                setMobile={setMobile}
                                email={email}
                                setEmail={setEmail}
                                banks={banks}
                                branches={branches}
                                walletProviders={walletProviders}
                            />

                            <div className="pt-6 flex gap-4">
                                <button
                                    type="button"
                                    onClick={() => window.history.back()}
                                    className="px-6 py-2 bg-[#D9D9D999] text-black font-[500] rounded-full"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={linking || updating}
                                    className="px-6 py-2 bg-black text-white font-[500] rounded-full disabled:opacity-50"
                                >
                                    {linking || updating ? "Saving..." : "Save"}
                                </button>
                            </div>
                        </div>
                    </form>

                    <div className="mt-10 pl-20">
                        <label className="block text-[16px] text-black/50 font-[500] mb-1">
                            Powered By
                        </label>
                        <Image
                            src={prefixBasePath("/spar_acc.png")}
                            alt="SPAR Logo"
                            width={100}
                            height={40}
                            className="object-contain"
                        />
                    </div>
                </div>

                <InfoSidebar
                    accountInfo={accountInfo}
                />
            </div>

            {showModal && (
                <AccountSuccessModal
                    onClose={() => setShowModal(false)}
                    onBack={() => window.history.back()}
                />
            )}
            {showErrorModal && <AccountErrorModal onClose={() => setShowErrorModal(false)} />}
            {showRemoveModal && (
                <AccountRemoveModal
                    onClose={() => setShowRemoveModal(false)}
                    onConfirm={() => setShowRemoveModal(false)}
                />
            )}
        </div>
    );
}
