'use client';
import { useRegisterSchema } from '../shared/hooks/useRegisterSchema';
import { useState, useEffect } from 'react';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useTranslations } from 'next-intl';

interface RegisterSchemaViewProps {
    registerId: string;
    activeTab: 'filter' | 'search' | 'deduplication';
}

export default function RegisterSchemaView({
    registerId,
    activeTab,
}: RegisterSchemaViewProps) {
    const t = useTranslations();
    const { schema, loading, refresh } = useRegisterSchema(registerId);
    const [editableSchema, setEditableSchema] = useState<string>('');
    const { execute: updateSchema, loading: updating } = useFetch();

    useEffect(() => {
        if (schema) {
            const rawSchema =
                activeTab === 'filter'
                    ? schema.filter_schema
                    : activeTab === 'search'
                        ? schema.search_result_schema
                        : schema.deduplicate_schema;
            setEditableSchema(JSON.stringify(rawSchema, null, 2));
        }
    }, [schema, activeTab]);

    const handleSave = async () => {

        let parsedSchema = null

        try {
            parsedSchema = JSON.parse(editableSchema);
        } catch (error) {
            toast.error(t('toast_invalid_schema'));
            return;
        }

        const result = await updateSchema('/api/configuration/registers/register-schema/update', {
            method: 'POST',
            body: JSON.stringify({
                register_id: registerId,
                filter_schema: activeTab === 'filter' ? parsedSchema : undefined,
                search_result_schema: activeTab === 'search' ? parsedSchema : undefined,
                deduplicate_schema: activeTab === 'deduplication' ? parsedSchema : undefined,
            }),
        });

        if (result) {
            toast.success(t('toast_schema_updated'));
            refresh?.();
        } else {
            toast.error(t('toast_schema_update_failed'));
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8 bg-neutral-second rounded-[10px] mx-7.5">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-second"></div>
            </div>
        );
    }


    if (!schema) {
        return <div className="p-6 text-neutral-first/50">{t('no_schema_found') || "No schema found"}</div>;
    }

    return (
        <div className="mx-7.5 bg-neutral-second rounded-[10px] p-6 relative">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-neutral-first capitalize">
                    {activeTab} {t('schema') || "Schema"}
                </h3>
                <button
                    onClick={handleSave}
                    className="bg-neutral-first text-neutral-second px-4 py-2 rounded-[10px] font-semibold"
                >
                    {t('save_schema') || "Save Schema"}
                </button>
            </div>
            <div className="border border-secondary-second rounded-[10px] bg-secondary-second/20 overflow-hidden">
                <textarea
                    value={editableSchema}
                    onChange={(e) => setEditableSchema(e.target.value)}
                    className="w-full min-h-125 p-4 font-mono text-sm text-neutral-first focus:outline-none resize-y"
                    spellCheck={false}
                />
            </div>
        </div>
    );
}
