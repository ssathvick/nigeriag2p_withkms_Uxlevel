'use client';
import { SectionBuilder } from '@openg2p/registry-widgets';
import type { SectionConfig } from '@openg2p/registry-widgets';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { useTranslations } from "next-intl";

interface SectionDetailsConfigViewProps {
    sectionUISchema: any;
    registerId: string;
    sectionId: string;
    isCoreSection?: boolean;
}

export default function SectionDetailsConfigView({
    sectionUISchema,
    registerId,
    sectionId,
    isCoreSection = false,
}: SectionDetailsConfigViewProps) {
    const t = useTranslations();
    const { execute: updateUISchema, loading } = useFetch();

    const handleSectionChange = (updatedSection: SectionConfig) => {
        //If required then perform some action on UI schema onchange.
    };

    const handleSave = async (updatedSection: SectionConfig) => {
        if (isCoreSection) {
            toast.info(t('core_section_warning') || 'This is a core section, UI schema cannot be modified.', {
                position: "top-right",
                className: 'rounded-[15px] shadow-xl border border-secondary-first',
            });
            return;
        }

        if (!registerId || !sectionId) {
            toast.error(t('toast_section_info_missing') || 'Missing required section information');
            return;
        }

        const result = await updateUISchema('/api/configuration/registers/section-metadata/update-section-ui-schema', {
            method: 'POST',
            body: JSON.stringify({
                section_id: sectionId,
                register_id: registerId,
                section_ui_schema: updatedSection,
            })
        });

        if (result?.section_id) {
            toast.success(t('toast_section_ui_updated') || 'Section UI schema updated successfully');
        } else {
            toast.error(t('toast_section_ui_update_failed') || 'Failed to update section UI schema');
        }
    };

    return (
        <div className='mx-8 mt-6 bg-neutral-second rounded-[10px] px-8 pb-8 pt-12 mb-6 overflow-x-visible'>
            <SectionBuilder
                initialSection={sectionUISchema}
                onChange={handleSectionChange}
                onSave={handleSave}
            />
        </div>

    );
}
