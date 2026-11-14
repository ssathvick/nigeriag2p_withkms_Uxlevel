'use client';

import { useMemo, useState } from 'react';
import { useTranslations } from 'next-intl';
import type { RegisterRecordField } from '@/features/configuration/shared/hooks/useRegisterRecordFields';
import {
    buildFilterPreviewLines,
    serializeFilterExpression,
    usesNoValue,
    type FilterRootState,
} from './policyFilterExpression';

type PreviewTab = 'summary' | 'json';

interface PolicyFilterPreviewProps {
    root: FilterRootState;
    fields: RegisterRecordField[];
}

export default function PolicyFilterPreview({ root, fields }: PolicyFilterPreviewProps) {
    const t = useTranslations();
    const [tab, setTab] = useState<PreviewTab>('summary');
    const previewLines = useMemo(() => buildFilterPreviewLines(root), [root]);

    const jsonPreview = useMemo(() => {
        try {
            return JSON.stringify(serializeFilterExpression(root, fields), null, 2);
        } catch {
            return '{}';
        }
    }, [root, fields]);

    const formatCondition = (fieldId: string, operator: string, valueInput: string) => {
        const opLabel = t(`filter_operator_${operator}`);
        if (usesNoValue(operator as Parameters<typeof usesNoValue>[0])) {
            return `${fieldId || '…'} · ${opLabel}`;
        }
        const value = valueInput.trim() || '…';
        return `${fieldId || '…'} · ${opLabel} · "${value}"`;
    };

    return (
        <div className="rounded-[10px] border border-primary-second/40 bg-secondary-first/40 p-4 flex flex-col gap-3 h-full min-h-[18rem]">
            <h3 className="text-base font-semibold text-neutral-first">{t('filter_preview')}</h3>

            <div className="flex rounded-[10px] border border-primary-second/50 p-0.5 bg-neutral-second">
                <button
                    type="button"
                    onClick={() => setTab('summary')}
                    className={`flex-1 rounded-[8px] px-3 py-2 text-sm font-semibold transition-colors ${
                        tab === 'summary'
                            ? 'bg-neutral-first text-neutral-second'
                            : 'text-neutral-first/60 hover:text-neutral-first'
                    }`}
                >
                    {t('filter_preview_summary')}
                </button>
                <button
                    type="button"
                    onClick={() => setTab('json')}
                    className={`flex-1 rounded-[8px] px-3 py-2 text-sm font-semibold transition-colors ${
                        tab === 'json'
                            ? 'bg-neutral-first text-neutral-second'
                            : 'text-neutral-first/60 hover:text-neutral-first'
                    }`}
                >
                    {t('filter_preview_json')}
                </button>
            </div>

            {tab === 'summary' ? (
                <div className="flex-1 min-h-[14rem] max-h-[32rem] overflow-y-auto">
                    {previewLines.length === 0 ? (
                        <p className="text-[16px] text-neutral-first/50">—</p>
                    ) : (
                        <ul className="space-y-2 text-[16px] text-neutral-first">
                            {previewLines.map((line, index) => {
                                if (line.kind === 'group') {
                                    return (
                                        <li
                                            key={`g-${index}`}
                                            className="font-medium text-neutral-first/80"
                                            style={{ paddingLeft: `${line.depth * 12}px` }}
                                        >
                                            {line.operator === 'AND'
                                                ? t('filter_logic_and')
                                                : t('filter_logic_or')}
                                        </li>
                                    );
                                }
                                return (
                                    <li
                                        key={`c-${index}`}
                                        style={{ paddingLeft: `${line.depth * 12}px` }}
                                    >
                                        {formatCondition(
                                            line.field_id,
                                            line.operator,
                                            line.valueInput,
                                        )}
                                    </li>
                                );
                            })}
                        </ul>
                    )}
                </div>
            ) : (
                <pre className="flex-1 min-h-[14rem] max-h-[32rem] overflow-auto rounded-[10px] border border-primary-second bg-neutral-second p-4 text-sm font-mono text-neutral-first leading-relaxed">
                    {jsonPreview}
                </pre>
            )}
        </div>
    );
}
