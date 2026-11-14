import labels from '../../../locales/registry-display-labels.json';

/** Translate display copy only; identifiers and persisted workflow codes stay unchanged. */
export function registryDisplayText(value: string): string {
    return (labels as Record<string, string>)[value] ?? value;
}
