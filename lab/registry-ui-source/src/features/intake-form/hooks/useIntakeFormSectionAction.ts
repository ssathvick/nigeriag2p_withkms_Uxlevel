import React, { useState, useEffect,useRef } from 'react';
import { useRouter } from '@/i18n/navigation';
import { useFetch } from '@/shared/hooks/useFetch';
import { toast } from 'react-toastify';
import { IntakeFormSection } from '../types/intake-form';
import ActionModal from '@/components/shared/ActionModal';
import type { SectionChanges } from '@openg2p/registry-widgets';
import { extractFilesFromSection, intakeNormalisedRecords } from '@/features/register/utils';
import { UploadedDocument } from '@/shared/types';
import { useTranslations } from 'next-intl';

interface UseIntakeFormSectionActionProps {
    registerId?: string;
    formId: string;
    registerType: string;
    section?: IntakeFormSection | null;
    submissionId?: string | null;
    onSuccess?: () => void;
}

export const useIntakeFormSectionAction = ({
    registerId,
    formId,
    registerType,
    section,
    submissionId = null,
    onSuccess
}: UseIntakeFormSectionActionProps) => {
    const t = useTranslations();
    const router = useRouter();
    const { execute: executeSave } = useFetch();
    const { execute: uploadDocumentRequest } = useFetch();

    const [activeSubmissionId, setActiveSubmissionId] = useState<string | null>(submissionId);
    const activeSubmissionIdRef=useRef<string|null>(submissionId);
    const [sectionInternalIds, setSectionInternalIds] = useState<Record<string, string>>({});
    const sectionInternalIdsRef=useRef<Record<string,string>>({});

    useEffect(() => {
        setActiveSubmissionId(submissionId);
        activeSubmissionIdRef.current=submissionId;
    }, [submissionId]);

    const [modalConfig, setModalConfig] = useState<{
        isOpen: boolean;
        type: 'warning' | 'success';
        title: string;
        subtitle: string;
        onConfirm?: () => void;
        onClose: () => void;
        confirmText?: string;
        cancelText?: string;
        hideCancel?: boolean;
    } | null>(null);

    const closeModal = () => {
        setModalConfig(null);
    };

    const performFinalize = async () => {
        const targetSubmissionId = activeSubmissionIdRef.current || submissionId;
        if (!targetSubmissionId || !registerId) return;

        try {
            if(registerType==='household'){
              const details=await executeSave('/api/intake-form/get-intake-form-submission',{method:'POST',body:JSON.stringify({submission_id:targetSubmissionId,register_id:registerId})});
              const section=details?.section_payloads?.find((s:any)=>s.section_register_id===registerId&&s.records?.length);
              const record=section?.records?.[0];
              if(!record){toast.error('Save household details before submitting.');return;}
              const confirmation=await executeSave('/api/intake-form/save-intake-form-submission',{method:'POST',body:JSON.stringify({submission_id:targetSubmissionId,register_id:registerId,form_id:formId,section_id:'hh_survey_consent',section_register_id:registerId,section_payload:[{...record,registration_confirmed:'YES',edit_action:'UPDATE'}]})});
              if(!confirmation||confirmation.error){toast.error('Could not save the household confirmation.');return;}
            }
            const saveResult = await executeSave('/api/intake-form/finalize-intake-form-submission', {
                method: 'POST',
                body: JSON.stringify({
                    submission_id: targetSubmissionId,
                    register_id: registerId,
                    form_id: formId,
                })
            });

            if (saveResult?.error) {
                toast.error(t('toast_operation_failed'));
                return;
            }

            const handleSuccessClose = () => {
                closeModal();
                router.push(`/intake-form/${registerType}`);
                if (onSuccess) onSuccess();
            };

            setModalConfig({
                isOpen: true,
                type: 'success',
                title: t('submitted_successfully'),
                subtitle: t('submitted_successfully_subtitle'),
                confirmText: t('close'),
                hideCancel: true,
                onClose: handleSuccessClose,
                onConfirm: handleSuccessClose
            });

        } catch (error) {
            toast.error(t('toast_form_save_error'));
        }
    };

    const performSave = async (change: SectionChanges, action: 'submit' | 'draft', actionSection?: IntakeFormSection) => {
        const activeSection = actionSection || section;
        if (!activeSection || !registerId) return;


        const files = change?.files ?? [];
        const { filesToUpload = [], fileLabels = [] } =
            extractFilesFromSection(files) || {};

        let documentsResponse: UploadedDocument[] = [];

        if (filesToUpload.length > 0) {
            try {
                for (let j = 0; j < filesToUpload.length; j++) {
                    const formData = new FormData();
                    formData.append("document_label", fileLabels[j]);
                    formData.append("documents", filesToUpload[j]);

                    const uploadResult = await uploadDocumentRequest(
                        "/api/change-request/upload-document",
                        {
                            method: "POST",
                            body: formData,
                        }
                    );

                    if (Array.isArray(uploadResult)) {
                        documentsResponse.push(...uploadResult);
                    } else if (uploadResult) {
                        documentsResponse.push(uploadResult);
                    }
                }
            } catch (error) {
                toast.error(t('toast_upload_failed'), {
                    position: "top-right",
                    autoClose: 6000,
                });
                console.error("File upload error:", error);
                return;
            }
        }

        // Keep existing documents that are already uploaded
        const existingDocuments = (change?.files || []).filter(file => file && typeof file === 'object' && ('document_store_id' in file));
        documentsResponse = [...existingDocuments as UploadedDocument[], ...documentsResponse];

        const savePayload = {
            submission_id: activeSubmissionIdRef.current || submissionId,
            section_id: activeSection.section_id,
            section_payload: intakeNormalisedRecords(change?.records, sectionInternalIdsRef.current[activeSection.section_register_id]),
            section_register_id: activeSection.section_register_id,
            form_id: formId,
            register_id: registerId,
            created_by: "TEST_USER" //TODO:add here original user name.

        };

        try {
            const saveResult = await executeSave('/api/intake-form/save-intake-form-submission', {
                method: 'POST',
                body: JSON.stringify(savePayload)
            });

            if (!saveResult || saveResult.error) {
                toast.error(t('toast_operation_failed'));
                return false;
            }

            if (saveResult && saveResult.submission_id) {
                setActiveSubmissionId(saveResult.submission_id);
                activeSubmissionIdRef.current=saveResult.submission_id;
            }

            // Extract and cache the internal_record_id for non-list sections from the response.
            // This ensures that subsequent draft saves, or other sections belonging to the same register,
            // will reuse the existing internal_record_id rather than creating duplicate records for the same section_register_id.
            if (saveResult && saveResult.section_payloads) {
                const currentSectionPayload = saveResult.section_payloads.find(
                    (payload: any) => payload.section_register_id === activeSection.section_register_id
                );

                if (currentSectionPayload && !currentSectionPayload.is_list && currentSectionPayload.records?.length > 0) {
                    sectionInternalIdsRef.current[activeSection.section_register_id]=currentSectionPayload.records[0].internal_record_id;
                    setSectionInternalIds(prev => ({
                        ...prev,
                        [activeSection.section_register_id]: currentSectionPayload.records[0].internal_record_id
                    }));
                }
            }

            if (action === 'draft') {
                toast.success(t('draft_updated_successfully'));
                if (onSuccess) onSuccess();
                return {saved:true,submission_id:activeSubmissionIdRef.current};
            }

            const handleSuccessClose = () => {
                closeModal();
                if (action === 'submit') {
                    router.push(`/intake-form/${registerType}`);
                }
                if (onSuccess) onSuccess();
            };

            setModalConfig({
                isOpen: true,
                type: 'success',
                title: t('submitted_successfully'),
                subtitle: t('submitted_successfully_subtitle'),
                confirmText: t('close'),
                hideCancel: true,
                onClose: handleSuccessClose,
                onConfirm: handleSuccessClose
            });

        } catch (error) {
            console.error('Native draft save failed',error);
            toast.error(t('toast_form_save_error'));
            return false;
        }
    };

    const handleAction = async (sectionChanges?: SectionChanges, action: 'submit' | 'draft' = 'submit', actionSection?: IntakeFormSection) => {
        const activeSection = actionSection || section;

        if (action === 'submit') {
            setModalConfig({
                isOpen: true,
                type: 'warning',
                title: t('are_you_sure'),
                subtitle: t('submit_confirmation_subtitle'),
                confirmText: t('submit'),
                cancelText: t('cancel'),
                onClose: closeModal,
                onConfirm: () => {
                    closeModal();
                    if (sectionChanges && activeSection) {
                        performSave(sectionChanges, 'submit', activeSection);
                    } else {
                        performFinalize();
                    }
                }
            });
        } else if (sectionChanges && activeSection) {
            return await performSave(sectionChanges, 'draft', activeSection);
        }
    };

    const FormActionModals = () => {
        if (!modalConfig) return null;
        return React.createElement(ActionModal, modalConfig);
    };

    return { handleAction, FormActionModals };
};
