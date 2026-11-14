export const REGISTRY_CHANGE_REQUEST_ARTIFACT = 'registry.change_request';
export const REGISTRY_INTAKE_FORM_ARTIFACT = 'registry.intake_form';

export const TASK_ARTIFACT_FILTER_OPTIONS = [
    {
        value: 'change_request',
        artifactType: REGISTRY_CHANGE_REQUEST_ARTIFACT,
    },
    {
        value: 'intake_form',
        artifactType: REGISTRY_INTAKE_FORM_ARTIFACT,
    },
] as const;

export type TaskArtifactFilterValue =
    (typeof TASK_ARTIFACT_FILTER_OPTIONS)[number]['value'];
