'use client';

import { useEffect } from 'react';
import { useTranslations } from 'next-intl';

import { useRouter } from '@/i18n/navigation';
import { AddTabModal} from '@/features/configuration/registers';
import { useParams } from 'next/navigation';
import { useConfigTabs } from '../shared/hooks/useConfigTabs';
import { useFetch } from '@/shared/hooks';
import { toast } from 'react-toastify';
import { CONFIGURATION_TABS_ACTIONS } from '../shared/utils/configurationTabs.actions';
import Can from '@/components/shared/Can';
import { DataTable, DeleteButton } from '../shared/components';
import ConfirmRemovePopup from '../shared/components/ConfirmRemovePopup';
import { useState } from 'react';

interface RegisterTabConfigViewProps {
	isModalOpen: boolean;
	onCloseModal: () => void;
	registerTabId?: string;
	page?: number;
	pageSize?: number;
	onDataLoaded?: (totalItems: number, currentCount: number) => void;
}

export default function RegisterTabConfigView({
	isModalOpen,
	onCloseModal,
	page = 1,
	pageSize = 10,
	onDataLoaded,
}: RegisterTabConfigViewProps) {
	const t = useTranslations();
	const router = useRouter();
	const { registerId } = useParams<{ registerId: string }>();
	const { tabs, loading, refresh, pagination } = useConfigTabs(registerId, page, pageSize);
	const [showDeletePopup, setShowDeletePopup] = useState(false);
	const [selectedTabId, setSelectedTabId] = useState<string | null>(null);


	// Effect to notify parent of pagination info
	useEffect(() => {
		if (pagination && onDataLoaded) {
			onDataLoaded(pagination.number_of_items, tabs.length);
		}
	}, [pagination, tabs.length, onDataLoaded]);


	const { execute: deleteTab } = useFetch();

	const proceedDelete = async (tabId: string) => {
		const result = await deleteTab('/api/configuration/registers/tab-metadata/delete-tab', {
			method: 'POST',
			body: JSON.stringify({ tab_id: tabId })
		});

		if (result) {
			toast.success(t('toast_tab_removed'));
			refresh();
		} else {
			toast.error(t('toast_tab_remove_failed'));
		}
	};

	const handleDelete = (tabId: string) => {
		setSelectedTabId(tabId);
		setShowDeletePopup(true);
	};

	const handleConfirmDelete = async () => {
		if (!selectedTabId) return;
		await proceedDelete(selectedTabId);
		setShowDeletePopup(false);
		setSelectedTabId(null);
	};

	const columns = [
		{
			key: 'tab_label',
			label: t('tab_label'),
		},
		{
			key: 'tab_order',
			label: t('tab_order'),
		},
		{
			key: 'is_active',
			label: 'Status',
			render: (item: any) =>
				item.is_active ? t('active') : t('inactive'),
		},
	];

	return (
		<>
			<DataTable
				columns={columns}
				data={tabs}
				loading={loading}
				rowKey={(item) => item.tab_id}
				onRowClick={(item) =>
					router.push(`/configuration/registers/${registerId}/tabs/${item.tab_id}`)
				}
				actions={(item) => (
					<Can action={CONFIGURATION_TABS_ACTIONS.delete}>
						<DeleteButton
							label={t('remove')}
							onClick={() => handleDelete(item.tab_id)}
						/>
					</Can>
				)}
			/>

			{isModalOpen && (
				<AddTabModal
					onClose={onCloseModal}
					onSuccess={refresh}
				/>
			)}

			{showDeletePopup && (
				<ConfirmRemovePopup
					onClose={() => {
						setShowDeletePopup(false);
						setSelectedTabId(null);
					}}
					onConfirm={handleConfirmDelete}
					messageKey='confirm_remove_tab'
				/>
			)}
		</>
	);
}
