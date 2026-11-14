'use client';

import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useConfigSections } from '../shared/hooks/useConfigSections';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';

import { useEffect, useState } from 'react';
import Can from '@/components/shared/Can';
import { CONFIGURATION_SECTIONS_ACTIONS } from '../shared/utils/configurationSections.actions';
import AddTabSectionModal from './AddTabSectionModal';
import EditTabSectionModal from './EditTabSectionModal';
import EditButton from '../shared/components/EditButton';
import { DataTable, DeleteButton } from '../shared/components';
import ConfirmRemovePopup from '../shared/components/ConfirmRemovePopup';

interface RegisterTabSectionConfigViewProps {
    isModalOpen: boolean;
    onCloseModal: () => void;
    page?: number;
    pageSize?: number;
    onDataLoaded?: (totalItems: number, currentCount: number) => void;
}

export default function RegisterTabSectionConfigView({
    isModalOpen,
    onCloseModal,
    page = 1,
    pageSize = 10,
    onDataLoaded,
}: RegisterTabSectionConfigViewProps) {
    const t = useTranslations();
    const { registerId, tabId } = useParams<{ registerId: string; tabId: string }>();
    const { sections, loading, refresh, pagination } = useConfigSections(tabId, page, pageSize);

    const [editModalOpen, setEditModalOpen] = useState(false);
    const [selectedSection, setSelectedSection] = useState<any>(null);
    const [showDeletePopup, setShowDeletePopup] = useState(false);
    const [selectedTabSectionId, setSelectedTabSectionId] = useState<string | null>(null);

    const handleEdit = (section: any) => {
        setSelectedSection(section);
        setEditModalOpen(true);
    };

    useEffect(() => {
        if (pagination && onDataLoaded) {
            onDataLoaded(pagination.number_of_items, sections.length);
        }
    }, [pagination, sections.length, onDataLoaded]);

    const { execute: deleteSection } = useFetch();


    const proceedDelete = async (tab_section_id: string) => {
        const result = await deleteSection('/api/configuration/registers/tab-metadata/remove-section', {
            method: 'POST',
            body: JSON.stringify({ tab_section_id: tab_section_id })
        });

        if (result) {
            toast.success(t('toast_section_removed'));
            refresh();
        } else {
            toast.error(t('toast_section_remove_failed'));
        }
    };

    const handleDelete = (section: any) => {
        setSelectedTabSectionId(section.tab_section_id);
        setShowDeletePopup(true);
    };

    const handleConfirmDelete = async () => {
        if (!selectedTabSectionId) return;
        await proceedDelete(selectedTabSectionId);
        setShowDeletePopup(false);
        setSelectedTabSectionId(null);
    };

    const columns = [
        {
            key: 'section_id',
            label: t('section_id'),
        },
        {
            key: 'section_order',
            label: t('section_order'),
        },
    ];

    return (
        <>
            <DataTable
                columns={columns}
                data={sections}
                loading={loading}
                rowKey={(item) => item.tab_section_id}
                actions={(item) => (
                    <div className="flex gap-4">
                        <Can action={CONFIGURATION_SECTIONS_ACTIONS.delete}>
                            <EditButton
                                label={t('edit')}
                                onClick={() => handleEdit(item)}
                            />
                        </Can>

                        <Can action={CONFIGURATION_SECTIONS_ACTIONS.delete}>
                            <DeleteButton
                                label={t('remove')}
                                onClick={() => handleDelete(item)}
                            />
                        </Can>
                    </div>
                )}
            />

            {isModalOpen && (
                <AddTabSectionModal
                    onClose={onCloseModal}
                    onSuccess={refresh}
                />
            )}
            {editModalOpen && (
                <EditTabSectionModal
                    onClose={() => setEditModalOpen(false)}
                    onSuccess={refresh}
                    initialData={selectedSection}
                />
            )}
            {showDeletePopup && (
                <ConfirmRemovePopup
                    onClose={() => {
                        setShowDeletePopup(false);
                        setSelectedTabSectionId(null);
                    }}
                    onConfirm={handleConfirmDelete}
                    messageKey='confirm_remove_section'
                />
            )}
        </>
    );
}
