"use client";

import { useParams } from "next/navigation";
import { ChangeRequestDetailsView } from "@/features/change-request/components";
import { useTranslations } from "next-intl";
import { useBreadcrumb } from "@/shared/hooks";
import { useRegisterRecord } from "@/context/RegisterRecordContext";

export default function RegisterChangeRequestDetailsPage() {
    const t = useTranslations();

    const { type: registerType, id: internalRecordId, changeId } = useParams<{
        type: string;
        id: string;
        changeId: string;
    }>();

    const { functionalRecordId, recordName } = useRegisterRecord();

    const breadcrumb = useBreadcrumb({
        registerType,
        functionalRecordId,
        recordName,
        internalRecordId,
        changeId,
        includeActiveTab: true,
        includeChangeRequest: true,
    });

    return (
        <ChangeRequestDetailsView
            changeId={changeId}
            breadcrumb={breadcrumb}
        />
    );
}
