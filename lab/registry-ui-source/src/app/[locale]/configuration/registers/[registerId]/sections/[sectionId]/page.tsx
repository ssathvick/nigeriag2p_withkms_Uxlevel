'use client';
import { useState } from 'react';

import { BreadcrumbBar } from '@/components/shared';
import { useParams } from 'next/navigation';
import {
    EditRegisterSectionModal,
    SectionDetailsConfigView
} from '@/features/configuration/registers';
import {
    ConfigDetailsSummary,
    useAllRegister,
    getRegisterDetails,
} from '@/features/configuration/shared';
import { useBreadcrumb } from '@/shared/hooks/useBreadcrumb';
import { useRbac } from '@/context/RbacContext';
import { CONFIGURATION_SECTIONS_ACTIONS } from '@/features/configuration/shared/utils/configurationSections.actions';
import { useTranslations } from 'next-intl';
import { useRegisterSection } from '@/features/configuration/shared/hooks/useRegisterSection';

const SectionConfigurationPage = () => {
    const t = useTranslations();
    const { registerId, sectionId } = useParams<{
        registerId: string;
        sectionId: string;
    }>();
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);

    const { can } = useRbac();
    const canEdit = can(CONFIGURATION_SECTIONS_ACTIONS.edit);


    const { registers, loading: registersLoading } = useAllRegister(1, 100);
    const { section, loading: sectionLoading, refresh } = useRegisterSection(registerId, sectionId)

    const registerDetails = getRegisterDetails(registerId, registers);

    const breadcrumb = useBreadcrumb({
        rootItem: { label: t('registers'), href: '/configuration/registers' },
        customItems: [
            { label: registerDetails.register_mnemonic || '', href: `/configuration/registers/${registerId}` },
            { label: section?.section_mnemonic || '', href: `/configuration/registers/${registerId}/sections/${sectionId}` }
        ]
    });

    const isLoading = registersLoading || sectionLoading;

    if (isLoading) {
        return (
            <div className="min-h-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-second"></div>
            </div>
        );
    }

    return (
        <>
            <div className="pt-4 px-7.5 mb-2 shrink-0">
                <BreadcrumbBar breadcrumb={breadcrumb} />
            </div>

            <ConfigDetailsSummary
                title={section.section_mnemonic || 'None'}
                description={section.section_description || 'None'}
                onEdit={
                    canEdit
                        ? () => setIsEditModalOpen(true)
                        : undefined
                }
            />

            <SectionDetailsConfigView
                sectionUISchema={section?.section_ui_schema}
                registerId={registerId || ''}
                sectionId={section?.section_id || ''}
                isCoreSection={section?.is_core_section}
            />

            {isEditModalOpen && (
                <EditRegisterSectionModal
                    initialData={section as any}
                    onClose={() => setIsEditModalOpen(false)}
                    onSuccess={refresh}
                />
            )}
        </>
    );
};

export default SectionConfigurationPage;
