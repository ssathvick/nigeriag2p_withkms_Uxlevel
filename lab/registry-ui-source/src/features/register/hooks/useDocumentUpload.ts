import { useCallback } from "react";
import { UploadedDocument } from "@/shared/types";
import { toast } from "react-toastify";
import { useTranslations } from "next-intl";

interface UploadDocumentOptions {
    file: File;
    label: string;
}

interface UseDocumentUploadReturn {
    uploadDocument: (options: UploadDocumentOptions) => Promise<UploadedDocument | null>;
    uploadDocuments: (options: UploadDocumentOptions[]) => Promise<UploadedDocument[]>;
}

export const useDocumentUpload = (
    uploadDocumentRequest: (url: string, options: RequestInit) => Promise<any>
): UseDocumentUploadReturn => {
    const t = useTranslations();

    const uploadDocument = useCallback(
        async ({ file, label }: UploadDocumentOptions): Promise<UploadedDocument | null> => {
            const formData = new FormData();
            formData.append("document_label", label);
            formData.append("documents", file);

            const uploadResult = await uploadDocumentRequest(
                "/api/change-request/upload-document",
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!uploadResult || (Array.isArray(uploadResult) && uploadResult.length === 0)) {
                return null;
            }

            return Array.isArray(uploadResult) ? uploadResult[0] : uploadResult;
        },
        [uploadDocumentRequest]
    );

    const uploadDocuments = useCallback(
        async (options: UploadDocumentOptions[]): Promise<UploadedDocument[]> => {
            const uploadedDocuments: UploadedDocument[] = [];

            for (const { file, label } of options) {
                const result = await uploadDocument({ file, label });
                if (result) {
                    uploadedDocuments.push(result);
                }
            }

            return uploadedDocuments;
        },
        [uploadDocument]
    );

    return { uploadDocument, uploadDocuments };
};
