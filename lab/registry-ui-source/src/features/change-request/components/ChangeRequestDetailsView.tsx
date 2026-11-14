"use client";

import { useMemo } from "react";
import {ReviewHistory} from '@/components/shared/ReviewHistory';
import Can from '@/components/shared/Can';
import {Link} from '@/i18n/navigation';

import { TabsLayout, ActionModal } from "@/components/shared";
import {
    ChangeRequestHeader,
    RejectReasonPopup,
} from "@/features/change-request/components";
import { ApprovalList, ApprovalListSkeleton } from "@/features/approval/components";


import {
    createWidgetStore,
} from "@openg2p/registry-widgets";
import { useTranslations } from "next-intl";
import { RegisterFlattenedRecord } from "@/features/register/types";
import { useChangeRequestManager, useRegisterSectionsFromCR } from "@/features/change-request/hooks";
import { useApprovals } from "@/features/approval/hooks/useApprovals";
import { parseAweCurrentStage } from "@/features/approval/utils/aweStatusSummary";
import { REGISTRY_CHANGE_REQUEST_ARTIFACT } from "@/features/approval/constants";
import { useFetch } from "@/shared/hooks/useFetch";
import { ChangeRequestValuesTabs } from "./ChangeRequestValuesTabs";
import CRHeaderSkeleton from "./CRHeaderSkeleton";
import SectionSchemaSkeleton from "./SectionSchemaSkeleton";

interface ChangeRequestSequenceCheck {
    change_request_id: string;
    internal_record_id: string;
    has_earlier_pending_change_requests: boolean;
    number_of_earlier_pending_change_requests: number;
    approval_decision_blocked: boolean;
}

interface Props {
    changeId: string;
    breadcrumb: { label: string; href?: string }[];
}

export default function ChangeRequestDetailsView({ changeId, breadcrumb }: Props) {
    const t = useTranslations();
    const {
        details,
        documents,
        loadingDetails,
        loadingDocuments,
        loadingAction,
        popupVisible,
        popupType,
        setPopupVisible,
        handleApprove,
        handleReject,
        submitReject,
        refetchDetails,
    } = useChangeRequestManager(changeId);

    const approvalArtifactContext = useMemo(() => {
        if (!details?.change_request_id) return null;
        const currentStage =
            parseAweCurrentStage(details.awe_request_status_summary) ?? 1;
        return {
            artifactId: details.change_request_id,
            artifactType: REGISTRY_CHANGE_REQUEST_ARTIFACT,
            currentStage,
        };
    }, [details?.change_request_id, details?.awe_request_status_summary]);

    const { tasks, loadingTasks, submitDecision } = useApprovals(
        details?.awe_request_id,
        approvalArtifactContext,
        refetchDetails,
    );

    const sequenceCheckOptions = useMemo(
        () => ({
            method: "POST" as const,
            body: JSON.stringify({ change_request_id: changeId }),
        }),
        [changeId],
    );

    const { data: sequenceCheckData, loading: loadingSequenceCheck } =
        useFetch<ChangeRequestSequenceCheck>({
            url: "/api/change-request/check-sequence",
            enabled: !!changeId,
            options: sequenceCheckOptions,
        });

    const approvalDecisionBlocked = sequenceCheckData?.approval_decision_blocked ?? false;

    const widgetStoreOld = useMemo(() => createWidgetStore(), []);
    const widgetStoreNew = useMemo(() => createWidgetStore(), []);
    const sectionId = details?.section_id;
    const sectionRegisterId = details?.section_register_id || "";
    const isListSection = details?.is_list || false;

    const { sectionUISchema, loadingSchema } = useRegisterSectionsFromCR({ sectionId });

    const newSectionData = useMemo(() => {
        if (!details?.change_payload?.length) return undefined;

        const map: Record<
            string,
            RegisterFlattenedRecord | { records: RegisterFlattenedRecord[] }
        > = {};

        if (isListSection === true) {
            map[sectionRegisterId] = {
                records: details.change_payload,
            };
        } else {
            map[sectionRegisterId] = details.change_payload[0];
        }

        return map;
    }, [details]);

    const oldSectionData = useMemo(() => {
        if (!details?.current_register_data?.length) return undefined;

        const map: Record<
            string,
            RegisterFlattenedRecord | { records: RegisterFlattenedRecord[] }
        > = {};

        if (isListSection === true) {
            map[sectionRegisterId] = {
                records: details.current_register_data,
            };
        } else {
            map[sectionRegisterId] = details.current_register_data[0];
        }

        return map;
    }, [details, isListSection, sectionRegisterId]);

    return (
        <TabsLayout breadcrumb={breadcrumb}>
            <div className="flex gap-7.5">
                <div className="w-full lg:w-[75%]">
                    {loadingDetails || loadingDocuments ? (
                        <CRHeaderSkeleton />
                    ) : (
                        details && (
                            <ChangeRequestHeader
                                details={details}
                                verificationCount={details.no_of_verifications_done ?? 0}
                                documents={documents}
                                onApprove={handleApprove}
                                onReject={handleReject}
                                loadingAction={loadingAction}
                            />
                        )
                    )}

                    <ReviewHistory events={details?.review_history}/>
                    {details?.awe_request_status_summary?.startsWith('returned') && <Can action="changeRequest:create"><div className="my-4 rounded-lg bg-amber-50 p-5"><p>This change request was returned for correction. Open the record, correct the same section and save to resubmit this request for independent review.</p><Link className="inline-block mt-3 rounded-full px-5 py-2 bg-neutral-first text-white" href={`/register/${details.register_mnemonic?.toLowerCase() || (details.register_id.endsWith('002')?'household':'individual')}/${details.internal_record_id}`}>Correct record details</Link></div></Can>}
                    {loadingSchema ? (
                        <SectionSchemaSkeleton />
                    ) : (
                        details && (
                            <ChangeRequestValuesTabs
                                widgetStoreNew={widgetStoreNew}
                                widgetStoreOld={widgetStoreOld}
                                newSectionData={newSectionData}
                                oldSectionData={oldSectionData}
                                sectionUISchema={sectionUISchema}
                                t={t}
                                changeId={changeId}
                            />
                        )
                    )}
                </div>

                <div className="w-full lg:w-[25%]">
                    {loadingDetails ||
                    loadingSequenceCheck ||
                    (!!details?.awe_request_id && loadingTasks) ? (
                        <ApprovalListSkeleton />
                    ) : (
                        <ApprovalList
                            tasks={tasks}
                            isPending={details?.approval_status === "PENDING"}
                            approvalDecisionBlocked={approvalDecisionBlocked}
                            onSubmitDecision={submitDecision}
                        />
                    )}
                </div>
            </div>
            {popupVisible && popupType === "reject-input" && (
                <RejectReasonPopup
                    onSubmit={(reason) => submitReject(reason)}
                    onClose={() => setPopupVisible(false)}
                    loading={loadingAction}
                />
            )}
        </TabsLayout>
    );
}
