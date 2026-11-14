"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "@/i18n/navigation";
import Forbidden from "./Forbidden";
import { useRbac } from "@/context/RbacContext";
import { checkPermission } from "@/shared/utils/checkPermission";
import { useTranslations } from "next-intl";


interface RequireActionProps {
    action?: string;
    anyOf?: readonly string[];
    allOf?: readonly string[];
    children: ReactNode;
    redirectTo?: string;
    forbiddenFallback?: ReactNode;
}

export default function RequireAction({
    action,
    anyOf,
    allOf,
    children,
    redirectTo,
    forbiddenFallback = <Forbidden />,
}: RequireActionProps) {
    const router = useRouter();
    const { loading, can, canAny, canAll } = useRbac();
    const t = useTranslations();

    const allowed = loading || checkPermission({ action, anyOf, allOf }, { can, canAny, canAll });

    useEffect(() => {
        if (!loading && !allowed && redirectTo) {
            router.replace(redirectTo);
        }
    }, [allowed, loading, redirectTo, router]);

    if (loading) {
        return (
            <div className="w-full min-h-screen flex items-center justify-center bg-neutral-second">
                <div className="flex flex-col items-center gap-4">
                    <img
                        src="/images/common/loading.gif"
                        alt="Loading"
                        className="w-12 h-12"
                    />
                    <p className="text-neutral-first/50 text-[20px]">{t('loading_admin')}</p>
                </div>
            </div>
        );
    }

    if (!allowed) {
        if (redirectTo) return null;
        return <>{forbiddenFallback}</>;
    }

    return <>{children}</>;
}
