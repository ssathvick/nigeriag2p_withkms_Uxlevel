'use client';

import { useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { toast } from 'react-toastify';

import { useFetch } from '@/shared/hooks';
import Can from '@/components/shared/Can';

import { CONFIGURATION_SECTIONS_ACTIONS } from '../shared/utils/configurationSections.actions';
import { Link, useRouter } from '@/i18n/navigation';
import { useAllRegisterSections } from '../shared/hooks/useAllRegisterSections';
import AddRegisterSectionModal from './AddRegisterSectionModal';
import { DataTable, DeleteButton } from '../shared/components';
import ConfirmRemovePopup from '../shared/components/ConfirmRemovePopup';
import { useState } from 'react';

interface RegisterSectionConfigViewProps {
	page?: number;
	pageSize?: number;
	onDataLoaded?: (totalItems: number, currentCount: number) => void;
	isModalOpen: boolean;
	onCloseModal: () => void;
}

export default function RegisterSectionConfigView({
	page = 1,
	pageSize = 10,
	onDataLoaded,
	isModalOpen,
	onCloseModal,
}: RegisterSectionConfigViewProps) {
	const t = useTranslations();
	const router = useRouter();
	const { registerId } = useParams<{ registerId: string }>();
	const [showDeletePopup, setShowDeletePopup] = useState(false);
	const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);

	const { sections, loading, pagination, refresh } = useAllRegisterSections(registerId, page, pageSize);

	useEffect(() => {
		if (pagination && onDataLoaded) {
			onDataLoaded(pagination.number_of_items, sections?.length || 0);
		}
	}, [pagination, sections?.length, onDataLoaded]);

	const { execute: deleteSection } = useFetch();

	const proceedDelete = async (sectionId: string) => {
		const result = await deleteSection(
			'/api/configuration/registers/section-metadata/delete-section',
			{
				method: 'POST',
				body: JSON.stringify({ section_id: sectionId })
			}
		);

		if (result) {
			toast.success(t('toast_section_removed'));
			refresh();
		} else {
			toast.error(t('toast_section_remove_failed'));
		}
	};

	const handleDelete = (sectionId: string) => {
		setSelectedSectionId(sectionId);
		setShowDeletePopup(true);
	};

	const handleConfirmDelete = async () => {
		if (!selectedSectionId) return;
		await proceedDelete(selectedSectionId);
		setShowDeletePopup(false);
		setSelectedSectionId(null);
	};

	const columns = [
		{
			key: 'section_mnemonic',
			label: t('section_mnemonic'),
		},
		{
			key: 'section_description',
			label: t('section_description'),
		},
	];

	return (
		<>
			<DataTable
				columns={columns}
				data={sections || []}
				loading={loading}
				rowKey={(item) => item.section_id}
				onRowClick={(item) =>
					router.push(`/configuration/registers/${registerId}/sections/${item.section_id}`)
				}
				actions={(item) => (
					<Can action={CONFIGURATION_SECTIONS_ACTIONS.delete}>
						<DeleteButton
							label={t('remove')}
							onClick={() => handleDelete(item.section_id)}
						/>
					</Can>
				)}
			/>
			{isModalOpen && (
				<AddRegisterSectionModal
					onClose={onCloseModal}
					onSuccess={refresh}
				/>
			)}
			{showDeletePopup && (
				<ConfirmRemovePopup
					onClose={() => {
						setShowDeletePopup(false);
						setSelectedSectionId(null);
					}}
					onConfirm={handleConfirmDelete}
					messageKey='confirm_remove_section'
				/>
			)}
		</>
	);
}
