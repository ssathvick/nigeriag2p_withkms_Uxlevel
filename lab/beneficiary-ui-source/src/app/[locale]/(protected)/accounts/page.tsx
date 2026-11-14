"use client";

import { useLocale } from "next-intl";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AuthUtil } from "@/features/auth/components";
import { useAuth } from "@/context/GlobalContext";

import { Loading } from "@/components";

import { prefixBasePath } from "@/shared/utils/path";

import {
    useUnlinkAccount,
    useResolveAccount,
} from "@/features/accountmapping/hooks";

import {
    AccountRemoveModal,
    AccountInfoSection,
    AccountSidebar,
    AccountEmptyState
} from "@/features/accountmapping/components";

import { getAccountInformation } from "@/features/accountmapping/utils";

export default function AccountsPage() {
    const lang = useLocale();
    AuthUtil({ failedRedirectUrl: `/${lang}/login` });

    const { profile } = useAuth();

    const router = useRouter();

    const { result, loading, handleResolve } = useResolveAccount();
    const { handleUnlink, unlinking } = useUnlinkAccount();

    const [showRemoveModal, setShowRemoveModal] = useState(false);

    const [accountInfo, setAccountInfo] = useState<any>(null);

    useEffect(() => {
        getAccountInformation()
            .then((data) => setAccountInfo(data))
            .catch(console.error);
    }, []);


    const confirmRemoveHandler = async () => {
        try {
            await handleUnlink();
            await handleResolve();
            setShowRemoveModal(false);
        } catch (err) {
            console.error("Failed to unlink account:", err);
        }
    };

    if (loading) {
        return <Loading title={"Account / Wallet"} height={"670px"} />
    }

    if (result?.type === "unknown") {
        return <AccountEmptyState lang={lang} />;
    }

    const profileImage = profile?.picture || prefixBasePath("/user_image.png");
    const profileName = profile?.name || "User"

    return (
        <>
            <div className="px-[50px] py-4 min-h-screen bg-white">
                <h1 className="text-[18px] font-[600] text-gray-800 mb-4">Account / Wallet</h1>

                <div className="flex flex-row rounded-[10px] drop-shadow-[0_4px_20px_rgba(0,0,0,0.25)] overflow-hidden">
                    <AccountInfoSection
                        profileImage={profileImage}
                        profileName={profileName}
                        result={result}
                    />
                    <AccountSidebar
                        accountInfo={accountInfo}
                        result={result}
                        unlinking={unlinking}
                        onEdit={() => router.push(`/${lang}/accounts/update`)}
                        onRemove={() => setShowRemoveModal(true)}
                    />
                </div>
            </div>

            {showRemoveModal && (
                <AccountRemoveModal
                    onClose={() => setShowRemoveModal(false)}
                    onConfirm={confirmRemoveHandler}
                />
            )}
        </>
    );
}
