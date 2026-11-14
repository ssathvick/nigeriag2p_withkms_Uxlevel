import { useCallback, useRef } from "react";
import { useFetch } from "@/shared/hooks/useFetch";
import { UploadedDocument } from "@/shared/types";
import { useRegister } from "@/context/RegisterContext";
import { useRegisterTabs } from "@/context/RegisterTabsContext";
import { useRegisterRecord } from "@/context/RegisterRecordContext";
import { SectionChanges } from "@openg2p/registry-widgets";
import { extractFilesFromSection, normalizeEditActions } from "../utils";
import { toast } from "react-toastify";
import { useTranslations } from "next-intl";
import { useDocumentUpload } from "./useDocumentUpload";
import { sectionChangePayload } from '../utils/sectionChangePayload';

import { TabSection } from "@/features/register/types";

export const useSectionSave = (
    onChangeRequestCreated: () => void,
    tabSections?: TabSection[]
) => {
    const t = useTranslations();
    const { internalRecordId } = useRegisterRecord();
    const { activeTabId } = useRegisterTabs();
    const { currentRegister } = useRegister();

    const { execute: submitChangeRequest } = useFetch();
    const { execute: uploadDocumentRequest } = useFetch();
    const { uploadDocument } = useDocumentUpload(uploadDocumentRequest);

    const isSubmitting = useRef(false);

    const handleSectionSave = useCallback(
        async (sectionChanges: SectionChanges) => {

            // prevent duplicate submission, when user click multiples time
            if (isSubmitting.current) return;

            if (!currentRegister || !internalRecordId) {
                return;
            }

            isSubmitting.current = true;
            try {

                const { register_id, register_mnemonic } = currentRegister;
                const { section_id, section_register_id, records: sectionChangeRecords, files } = sectionChanges;


                if (!section_id && !section_register_id) {
                    console.error(
                        t("toast_section_info_missing"),
                        { section_id, section_register_id }
                    );
                    return;
                }

                const { filesToUpload, fileLabels } = extractFilesFromSection(files);

                let documentsResponse: UploadedDocument[] = [];
                let document_store_id: string | undefined;

                // Profile pictures of register records
                if (sectionChanges.image) {
                    const uploadResult = await uploadDocument({
                        file: sectionChanges.image,
                        label: "profile_image_file",
                    });

                    if (uploadResult) {
                        documentsResponse.push(uploadResult);
                        document_store_id = uploadResult.document_store_id;

                        toast.success(t("toast_profile_image_upload_success"), {
                            position: "top-right",
                            autoClose: 4000,
                        });
                    }
                }

                if (filesToUpload.length > 0) {
                    try {
                        const uploadPromises = filesToUpload.map((file, index) =>
                            uploadDocument({
                                file,
                                label: fileLabels[index],
                            })
                        );

                        const results = await Promise.all(uploadPromises);
                        const successfulUploads = results.filter((r): r is UploadedDocument => r !== null);

                        if (successfulUploads.length === 0) {
                            toast.error(t("toast_upload_failed_cr_not_created"), {
                                position: "top-right",
                                autoClose: 6000,
                            });
                            return;
                        }

                        documentsResponse.push(...successfulUploads);

                        toast.success(t("toast_upload_success", { count: documentsResponse.length }), {
                            position: "top-right",
                            autoClose: 4000,
                        });
                    } catch (error) {
                        toast.error(t("toast_upload_failed"), {
                            position: "top-right",
                            autoClose: 6000,
                        });
                        console.error("File upload error:", error);
                        return;
                    }
                }

                const normalizedRecords = normalizeEditActions(
                    sectionChangeRecords,
                    internalRecordId,
                    document_store_id
                )

                const section = tabSections?.find(
                    (section) => section.section_id === section_id
                );
                const records = sectionChangePayload(section?.section_ui_schema ?? section?.section_data?.section_ui_schema, normalizedRecords);

                const endpoint = section?.is_core_section ? `/api/change-request/core-section/create` : `/api/change-request/create`;

                const change_request_response = await submitChangeRequest(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        register_id: register_id,
                        register_mnemonic: register_mnemonic,
                        internal_record_id: internalRecordId,
                        section_register_id: section_register_id,
                        tab_id: activeTabId,
                        section_id: section_id,
                        section_records: records,
                        // While creating change request
                        // via register always treated as
                        // Update action at chage request lavel
                        edit_action: "UPDATE",
                        documents: documentsResponse,
                    }),
                });

                if (change_request_response?.change_request_id) {
                    toast.success(t("toast_cr_created"), {
                        position: "top-right",
                        autoClose: 6000,
                    });
                    // Update the Pending change request count
                    onChangeRequestCreated();
                } else {
                    toast.error(t("toast_cr_create_failed"), {
                        position: "top-right",
                        autoClose: 6000,
                    });
                }
            } finally {
                isSubmitting.current = false;
            }
        },[
            currentRegister,
            internalRecordId,
            submitChangeRequest,
            activeTabId,
            uploadDocumentRequest,
            uploadDocument,
            onChangeRequestCreated,
            t,
            tabSections,
        ]
    );

    return { handleSectionSave };
};
