'use client';

import { useState } from 'react';
import { toast } from 'react-toastify';
import { useFileUrl } from '@/features/configuration/shared/hooks/useFileUrl';

interface Props {
    documentId?: string;
    label?: string;
    className?: string;
}

export default function FileLink({
    documentId,
    className,
}: Props) {
    const { getFileUrl } = useFileUrl();

    const handleClick = async (e: React.MouseEvent) => {
        e.stopPropagation();

        if (!documentId) return;

        const url = await getFileUrl(documentId);

        if (url) {
            window.open(url, '_blank');
        } else {
            toast.error('Failed to open file');
        }
    };

    if(!documentId)return null;
    return (
        <button
            onClick={handleClick}
            disabled={!documentId}
            className={`text-neutral-first hover:text-toast-info hover:underline transition-colors truncate disabled:opacity-50 ${className}`}
        >
            {documentId}
        </button>
    );
}
