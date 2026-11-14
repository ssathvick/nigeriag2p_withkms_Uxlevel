import { deserializeFile } from '@/shared/types';
import { DisplayField } from '../types';

export const sortedDisplayFields = (fields: DisplayField[]): DisplayField[] => {
    return [...fields].sort((firstField, secondField) => firstField.order - secondField.order);
};

export const extractFilesFromSection = (files?: unknown[]) => {
    const filesToUpload: File[] = [];
    const fileLabels: string[] = [];

    if (Array.isArray(files)) {
        files.forEach((value, index) => {
            if (value && typeof value === 'object' && (value as any).__type === 'File') {
                try {
                    const realFile = deserializeFile(value);
                    filesToUpload.push(realFile);

                    // Use embedded label if present, otherwise fallback to index-based label
                    const label = (value as any).label || (value as any).name || `file_${index}`;
                    fileLabels.push(label);
                } catch (error) {
                    console.error('Failed to deserialize file:', error);
                }
            }
        });
    }

    return {
        filesToUpload,
        fileLabels,
    };
};

/**
 * Section Change edit_action values:
 * - NO_CHANGE: No changes made (handled here)
 * - ADD: New record added (handled at widget level;
 *   only additional info such as IDs and required fields are added)
 * - DELETE: Record deleted (handled at registry widget level)
 * - UPDATE: Existing record updated (handled at registry widget level)
 */
export function normalizeEditActions(
    records: any[],
    linkInternalRecordId = "",
    document_store_id?: string,
) {
    if (!Array.isArray(records)) return [];

    return records.map((record) => {
        // TODO: Need to resolve 3-level structure
        const result = { ...record };

        if (result.edit_action === undefined) {
            result.edit_action = "NO_CHANGE";
        }

        if (result.edit_action === "ADD") {
            result.link_internal_record_id = linkInternalRecordId;
            result.internal_record_id = "";
        }

        if (document_store_id && result.record_image_storage_id !== undefined) {
            result.record_image_storage_id = document_store_id;
        }

        return result;
    });
}


export function intakeNormalisedRecords(records: any[], InternalRecordId?: string) {
    if (!Array.isArray(records)) return [];

    return records.map((record) => {
        const result = { ...record };

        if (result.edit_action == null) {
            result.edit_action = "ADD";
            result.link_internal_record_id = "";
            result.internal_record_id = "";
        }

        if (InternalRecordId && !result.internal_record_id) {
            result.internal_record_id = InternalRecordId;
        }

        return result;
    });
}
