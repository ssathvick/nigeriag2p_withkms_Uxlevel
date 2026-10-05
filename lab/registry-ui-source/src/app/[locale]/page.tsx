'use client';

import { useState } from 'react';
import { useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import {
    StatsCardLarge,
    StatsCardSmall,
    StatsCardsCarousel,
    SearchBarDropdown,
    SearchBar,
} from '@/components/ui';
import { getTasksListPath } from '@/features/approval/utils/taskNavigation';
import Image from 'next/image';

import { useRegister } from '@/context/RegisterContext';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';

import { REGISTER_ACTIONS } from '@/features/register/utils/register.actions';
import { INTAKE_FORM_ACTIONS } from '@/features/intake-form/utils/intakeForm.actions';
import { CHANGE_REQUEST_ACTIONS } from '@/features/change-request/utils/changeRequest.actions';
import { INCOMING_MESSAGE_ACTIONS } from '@/features/messages/utils/incomingMessage.actions';
import { OUTGOING_MESSAGE_ACTIONS } from '@/features/messages/utils/outgoingMessage.actions';
import { TASK_ARTIFACT_FILTER_OPTIONS } from '@/features/approval/constants';
import { VERIFICATION_CHANGE_REQUEST_ACTIONS } from '@/features/change-request/utils/verificationChangeRequest.actions';
import { VERIFICATION_INTAKE_FORM_ACTIONS } from '@/features/intake-form/utils/verificationIntakeForm.actions';
import Can from '@/components/shared/Can';


type ActiveStatsCard =
    | 'registers'
    | 'intake-form'
    | 'change-request'
    | 'messages'
    | 'tasks';

const ALL_CARDS: ActiveStatsCard[] = [
    'registers',
    'intake-form',
    'change-request',
    'tasks',
    'messages',
];

const LIMITED_CARDS: ActiveStatsCard[] = [
    'registers',
    'change-request',
    'tasks',
];

export default function Home() {
    const router = useRouter();
    const t = useTranslations();
    const { config } = useRuntimeConfig();

    const statsCardVariant = config?.partnerImportExportEnable ? 'small' : 'large';
    const visibleCards = statsCardVariant === 'small' ? ALL_CARDS : LIMITED_CARDS;

    const [activeStatsCard, setActiveStatsCard] =
        useState<ActiveStatsCard>('registers');
    const [selectedRegister, setSelectedRegister] = useState('select');
    const [selectedMessageType, setSelectedMessageType] = useState('incoming');
    const [selectedTaskArtifact, setSelectedTaskArtifact] = useState('change_request');

    const messageTypeOptions = [
        { value: 'incoming', label: t('incoming_messages') },
        { value: 'outgoing', label: t('outgoing_messages') },
    ];


    const { registers } = useRegister();

    const registerList =
        registers.map(r => ({
            value: r.register_mnemonic.toLowerCase(),
            label: t(r.register_subject),
        }));

    const taskArtifactOptions = TASK_ARTIFACT_FILTER_OPTIONS.map((opt) => ({
        value: opt.value,
        label:
            opt.value === 'change_request'
                ? t('change_requests')
                : t('intake_submissions'),
    }));

    const searchPlaceholders: Record<ActiveStatsCard, string> = {
        'registers': t('search_registers'),
        'intake-form': t('search_intake_form'),
        'change-request': t('search_change_requests'),
        'messages': t('search_messages'),
        'tasks': t('search_approval_tasks'),
    };

    const handleSearch = (value: string, register?: string) => {
        const searchValue = value.trim();

        const params = new URLSearchParams();
        if (searchValue) {
            params.set('search', searchValue);
        }
        params.set('page', '1');

        const query = params.toString();

        if (activeStatsCard === 'registers' || activeStatsCard === 'intake-form') {
            const selected =
                register && register !== 'select'
                    ? register
                    : registerList[0]?.value;

            if (!selected) return;

            const basePath =
                activeStatsCard === 'registers'
                    ? `/register/${selected}`
                    : `/intake-form/${selected}`;

            router.push(query ? `${basePath}?${query}` : basePath);
            return;
        }

        if (activeStatsCard === 'messages') {
            const type = selectedMessageType || 'incoming';

            const basePath =
                type === 'incoming'
                    ? '/incoming-messages'
                    : '/outgoing-messages';

            router.push(query ? `${basePath}?${query}` : basePath);
            return;
        }

        if (activeStatsCard === 'tasks') {
            const taskBase = getTasksListPath(
                selectedTaskArtifact as 'change_request' | 'intake_form',
            );
            const taskQuery = params.toString();
            router.push(taskQuery ? `${taskBase}?${taskQuery}` : taskBase);
            return;
        }

        const routeMap: Record<
            Exclude<ActiveStatsCard, 'registers' | 'intake-form' | 'messages' | 'tasks'>,
            string
        > = {
            'change-request': '/change-request'
        };
        router.push(
            query
                ? `${routeMap[activeStatsCard]}?${query}`
                : routeMap[activeStatsCard]
        );
    };

    const StatsCardComponent =
        statsCardVariant === 'small'
            ? StatsCardSmall
            : StatsCardLarge;


    const getViewAction = (
        activeStatsCard: ActiveStatsCard,
        selectedMessageType: string
    ) => {
        switch (activeStatsCard) {
            case "registers":
                return REGISTER_ACTIONS.view;
            case "intake-form":
                return INTAKE_FORM_ACTIONS.view;
            case "change-request":
                return CHANGE_REQUEST_ACTIONS.view;
            case "messages":
                return selectedMessageType === "incoming"
                    ? INCOMING_MESSAGE_ACTIONS.view
                    : OUTGOING_MESSAGE_ACTIONS.view;
        }
    };

    const viewAction = getViewAction(activeStatsCard, selectedMessageType);
    const taskSearchAnyOf = [
        VERIFICATION_CHANGE_REQUEST_ACTIONS.create,
        VERIFICATION_INTAKE_FORM_ACTIONS.create,
    ];

    const statsEndpointFor = (type: ActiveStatsCard) =>
        `/api/stats/${type === 'registers' ? 'register' : type === 'tasks' ? 'tasks' : type}`;

    const useStatsCarousel =
        statsCardVariant === 'small' && visibleCards.length > 4;

    return (
        <div className="min-h-screen bg-primary-first pt-8 sm:pt-10 md:pt-12 overflow-hidden text-secondary-second-900 bg-[url('/images/common/bg_pattern.png')]">
            <div className="relative">
                <div className="mx-auto flex max-w-6xl flex-col items-center px-4 sm:px-6 py-8 sm:py-10 lg:py-12 space-y-10 sm:space-y-12 lg:space-y-14">

                    {/* stats cards */}
                    {useStatsCarousel ? (
                        <StatsCardsCarousel
                            cards={visibleCards}
                            activeCard={activeStatsCard}
                            onSelectCard={setActiveStatsCard}
                            StatsCardComponent={StatsCardComponent}
                            statsEndpointFor={statsEndpointFor}
                        />
                    ) : (
                        <div
                            className={`flex flex-wrap items-stretch gap-4 sm:gap-5 lg:gap-6 ${statsCardVariant === 'small' ? 'w-full justify-center' : 'w-4/5 justify-between'}`}
                        >
                            {visibleCards.map((type) => (
                                <button
                                    key={type}
                                    type="button"
                                    onClick={() => setActiveStatsCard(type)}
                                    className={`bg-transparent p-0 text-left ${statsCardVariant === 'small' ? 'flex-1 min-w-40 sm:min-w-45 lg:min-w-55' : 'w-[calc(50%-12px)] sm:w-[calc(50%-10px)] lg:w-[calc(50%-12px)]'}`}
                                >
                                    <StatsCardComponent
                                        stats_endpoint={statsEndpointFor(type)}
                                        active={activeStatsCard === type}
                                    />
                                </button>
                            ))}
                        </div>
                    )}
                    <Can
                        action={activeStatsCard === 'tasks' ? undefined : viewAction}
                        anyOf={activeStatsCard === 'tasks' ? taskSearchAnyOf : undefined}
                        fallback={
                            <div className="relative border border-primary-second flex h-14 w-4/5 items-center rounded-[10px] bg-neutral-second overflow-visible">
                                <div className="relative flex items-center w-full h-full">
                                    <SearchBar
                                        placeholder={searchPlaceholders[activeStatsCard]}
                                        category={selectedRegister}
                                        onSearch={() => { }}
                                    />
                                    <div className="absolute inset-0 z-10 cursor-not-allowed" />
                                </div>
                            </div>
                        }
                    >
                        <div className="relative border border-primary-second flex h-14 w-4/5 items-center rounded-[10px] bg-neutral-second overflow-visible">

                            {(activeStatsCard === 'registers' || activeStatsCard === 'intake-form') &&
                                registerList?.length > 0 && (
                                    <SearchBarDropdown
                                        options={registerList}
                                        selected={selectedRegister}
                                        onChange={setSelectedRegister}
                                    />
                                )}

                            {activeStatsCard === 'messages' && (
                                <SearchBarDropdown
                                    options={messageTypeOptions}
                                    selected={selectedMessageType}
                                    onChange={setSelectedMessageType}
                                />
                            )}

                            {activeStatsCard === 'tasks' && (
                                <SearchBarDropdown
                                    options={taskArtifactOptions}
                                    selected={selectedTaskArtifact}
                                    onChange={setSelectedTaskArtifact}
                                />
                            )}

                            <SearchBar
                                placeholder={searchPlaceholders[activeStatsCard]}
                                category={selectedRegister}
                                onSearch={handleSearch}
                            />
                        </div>
                    </Can>
                </div>
                <div className="bottom-0 w-full px-4">
                    <Image
                        src={config?.branding?.dashboard_image || "/images/common/people.svg"}
                        alt={t('peoples_image_alt')}
                        width={1200}
                        height={600}
                        className="w-full h-auto select-none"
                        priority
                        unoptimized={!!config?.branding?.dashboard_image}
                    />
                </div>
            </div>
        </div>
    );
}