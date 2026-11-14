'use client';
import {useConfigurationAccess} from './configurationAccess';
import {useRbac} from '@/context/RbacContext';
import React from 'react';
import { Pencil, Eye } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface ConfigDetailsSummaryProps {
    title: string;
    description?: string;
    extraInfo1?: string;
    extraInfo2?: string;
    onEdit?: () => void;
    onView?: () => void;
}

export default function ConfigDetailsSummary({
    title,
    description,
    extraInfo1,
    extraInfo2,
    onEdit,
    onView
}: ConfigDetailsSummaryProps) {
    const t = useTranslations();const access=useConfigurationAccess();const {can}=useRbac();

    return (
        <div className="config-details-summary mx-8 mb-0">
            <div
                className="bg-primary-first/20 border-primary-second border-dashed border rounded-[10px] px-12 h-15 flex items-center justify-between shadow-sm"
                style={{ borderStyle: 'dashed', borderWidth: '1px' }}
            >
                <div className="flex flex-1 items-center gap-10">
                    <div className="min-w-30">
                        <span className="text-neutral-first/70 font-medium text-base">{title}</span>
                    </div>

                    <div className="flex-1 max-w-75 truncate">
                        <span className="text-neutral-first/70 text-sm">{description}</span>
                    </div>

                    {extraInfo1 && (
                        <div className="flex-1 truncate">
                            <span className="text-neutral-first/70 text-sm">{extraInfo1}</span>
                        </div>
                    )}
                    {extraInfo2 && (
                        <div className="flex-1 truncate">
                            <span className="text-neutral-first/70 text-sm">{extraInfo2}</span>
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-3 ml-8">
                    {onView && (
                        <button
                            onClick={onView}
                            className="bg-neutral-second p-2 rounded-[10px] hover:bg-secondary-first transition-colors shadow-sm flex items-center justify-center shrink-0"
                            title={t('view_details') || "View Details"}
                        >
                            <Eye size={16} className="text-neutral-first" />
                        </button>
                    )}
                    {onEdit && (!access||can(access.edit)) && (
                        <button
                            onClick={onEdit}
                            className="bg-neutral-second p-2 rounded-[10px] hover:bg-secondary-first transition-colors shadow-sm flex items-center justify-center shrink-0"
                            title={t('common.edit') || "Edit"}
                        >
                            <Pencil size={16} className="text-neutral-first" />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
