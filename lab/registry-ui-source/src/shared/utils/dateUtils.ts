
export function formatDateTime(value?: string | null) {
    if (!value) return '-- -- ----';

    // Handle various string formats
    let safeValue = value;
    if (!safeValue.includes('T') && safeValue.includes(' ')) {
        safeValue = safeValue.replace(' ', 'T');
    }

    // Force UTC if no timezone info
    if (!safeValue.includes('Z') && !safeValue.includes('+')) {
        safeValue = `${safeValue}Z`;
    }

    const date = new Date(safeValue);
    if (isNaN(date.getTime())) return '-- -- ----';

    return date.toLocaleString(undefined, {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
    });
}

export function formatDate(value?: string | null) {
    if (!value) return '-- -- ----';

    let safeValue = value;
    if (!safeValue.includes('T') && safeValue.includes(' ')) {
        safeValue = safeValue.replace(' ', 'T');
    }

    const [dp, tp] = safeValue.split(/[T ]/);
    const [y, m, d] = dp.split('-').map(Number);
    const [h, mi] = (tp || '00:00').split(':').map(Number);

    const date = new Date(y, m - 1, d, h, mi);
    if (isNaN(date.getTime())) return '-- -- ----';

    return date.toLocaleDateString();
}
