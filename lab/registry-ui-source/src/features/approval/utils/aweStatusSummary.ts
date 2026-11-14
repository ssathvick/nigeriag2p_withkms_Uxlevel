/** Parse registry ``awe_request_status_summary`` (e.g. ``in_review-stage2``). */
export function parseAweCurrentStage(summary?: string | null): number | undefined {
    if (!summary) return undefined;
    const match = summary.trim().match(/-stage(\d+)$/);
    return match ? Number(match[1]) : undefined;
}
