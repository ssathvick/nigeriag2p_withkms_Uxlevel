import { ApprovalTask } from '@/features/approval/types/approval';
import {
    REGISTRY_CHANGE_REQUEST_ARTIFACT,
    REGISTRY_INTAKE_FORM_ARTIFACT,
} from '@/features/approval/constants';

export function getTaskDetailHref(
    task: ApprovalTask,
    registerMnemonicById: Map<string, string>,
): string | null {
    const artifactId = task.artifact_id;
    if (!artifactId) return null;

    if (task.artifact_type === REGISTRY_CHANGE_REQUEST_ARTIFACT) {
        return `/tasks/change-request/${artifactId}`;
    }

    if (task.artifact_type === REGISTRY_INTAKE_FORM_ARTIFACT) {
        const contextMnemonic = task.context?.register_mnemonic;
        if (typeof contextMnemonic === 'string' && contextMnemonic.trim()) {
            return `/tasks/intake-form/${contextMnemonic.toLowerCase()}/${artifactId}`;
        }
        const registerId = task.context?.register_id;
        if (typeof registerId === 'string') {
            const mnemonic = registerMnemonicById.get(registerId);
            if (mnemonic) {
                return `/tasks/intake-form/${mnemonic}/${artifactId}`;
            }
        }
    }

    return null;
}

export function getTasksListPath(artifactFilter: 'change_request' | 'intake_form'): string {
    if (artifactFilter === 'intake_form') return '/tasks/intake-form';
    return '/tasks/change-request';
}

export function getTaskListLabel(task: ApprovalTask, t: (key: string) => string): string {
    const id = task.artifact_id ?? task.id;
    if (task.artifact_type === REGISTRY_INTAKE_FORM_ARTIFACT) {
        return `${t('intake_submission')}: ${id}`;
    }
    if (task.artifact_type === REGISTRY_CHANGE_REQUEST_ARTIFACT) {
        return `${t('change_request')}: ${id}`;
    }
    return task.search_text?.slice(0, 80) || id;
}
