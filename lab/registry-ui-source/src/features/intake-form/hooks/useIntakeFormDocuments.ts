import { useState, useEffect } from 'react';
import { useFetch } from '@/shared/hooks/useFetch';
import { UploadedDocument } from '@/shared/types';

export interface IntakeFormDocument extends UploadedDocument {
    document_url?: string;
}

export function useIntakeFormDocuments(documents: UploadedDocument[]) {
    const [docsWithUrls, setDocsWithUrls] = useState<IntakeFormDocument[]>([]);
    const { execute: getUrl } = useFetch({ enabled: false });

    useEffect(() => {
        if (!documents || documents.length === 0) {
            setDocsWithUrls([]);
            return;
        }

        const fetchUrls = async () => {
            try {
                const results: IntakeFormDocument[] = [];
                for (const doc of documents) {
                    try {
                        const response = await getUrl('/api/intake-form/get-file-url', {
                            method: 'POST',
                            body: JSON.stringify({ document_store_id: doc.document_store_id }),
                        });
                        results.push({
                            ...doc,
                            document_url: response?.file_url
                        });
                    } catch (e) {
                        console.error('Failed to fetch URL for document:', doc.document_store_id, e);
                        results.push({ ...doc });
                    }
                }
                setDocsWithUrls(results);
            } finally {
            }
        };

        fetchUrls();
    }, [documents]);

    return { documents: docsWithUrls };
}
