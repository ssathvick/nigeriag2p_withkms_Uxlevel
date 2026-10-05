import { Link } from '@/i18n/navigation';
import Image from 'next/image';
import { useTranslations } from 'next-intl';

interface SubOption {
    id: string;
    label: string;
    path: string;
}

interface SidebarOption {
    id: string;
    label: string;
    iconUrl: string;
    path: string;
    subOptions?: SubOption[];
}

const sidebarOptions: SidebarOption[] = [
    {
        id: 'registry',
        label: 'registry',
        iconUrl: "/images/config/menu_registry_01.png",
        path: '/configuration/registry/details',
        subOptions: [
            { id: 'registry-details', label: 'registry_details', path: '/configuration/registry/details' },
            { id: 'registry-themes', label: 'registry_theme', path: '/configuration/registry/themes' },
            { id: 'registry-languages', label: 'registry_languages', path: '/configuration/registry/languages' },
        ]
    },
    {
        id: 'registers',
        label: 'registers',
        iconUrl: "/images/config/menu_registers_02.png",
        path: '/configuration/registers'
    },
    {
        id: 'intake-forms',
        label: 'intake_forms',
        iconUrl: "/images/config/menu_intake_forms.png",
        path: '/configuration/intake-forms'
    },
    {
        id: 'data-models',
        label: 'data_models',
        iconUrl: "/images/config/menu_data_models_03.png",
        path: '/configuration/data-models'
    },
    {
        id: 'ingest-configurations',
        label: 'ingest_configurations',
        iconUrl: "/images/config/menu_ingest_config_04.png",
        path: '/configuration/ingest-configurations/key-paths',
        subOptions: [
            { id: 'ingest-key-paths', label: 'ingest_key_paths', path: '/configuration/ingest-configurations/key-paths' },
            { id: 'ingest-semantic-patterns', label: 'ingest_semantic_patterns', path: '/configuration/ingest-configurations/semantic-patterns' },
            { id: 'ingest-manage-subscription', label: 'ingest_manage_subscription', path: '/configuration/ingest-configurations/manage-subscription' },
            { id: 'ingest-templates', label: 'ingest_templates', path: '/configuration/ingest-configurations/templates' },
        ]
    },
    {
        id: 'outgest-configurations',
        label: 'outgest_configurations',
        iconUrl: "/images/config/menu_outgest_config_05.png",
        path: '/configuration/outgest-configurations/topics',
        subOptions: [
            { id: 'outgest-topics', label: 'outgest_topics', path: '/configuration/outgest-configurations/topics' },
            { id: 'outgest-templates', label: 'outgest_templates', path: '/configuration/outgest-configurations/templates' },
        ]
    },
    {
        id: 'data-policies',
        label: 'data_policies',
        iconUrl: "/images/config/menu_data_policies.png",
        path: '/configuration/data-policies'
    },
    {   id: 'awe-policy-config',
        label: 'awe_policy_configurations',
        iconUrl: '/images/config/menu_policy_configuration_08.png',
        path: '/configuration/awe-policy-config',
    },
];

export default function ConfigSidebar({ activeOption }: { activeOption: string }) {
    const t = useTranslations();
    return (
        <div className="w-full h-full bg-primary-first rounded-r-[10px] p-4 pt-8">
            <div className="space-y-2">
                {sidebarOptions.map((option) => {
                    const isParentActive = activeOption === option.id;
                    const isSubOptionActive = option.subOptions?.some(sub => activeOption === sub.id);
                    const isActive = isParentActive || isSubOptionActive;

                    return (
                        <div key={option.id} className="relative">
                            {isActive && (
                                <div
                                    className="absolute inset-0 rounded-[10px] bg-neutral-second/30"
                                />
                            )}

                            <div className="relative z-10">
                                <Link
                                    href={option.path}
                                    className="flex items-center px-4 py-3 cursor-pointer"
                                >
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${isActive ? 'bg-neutral-first' : 'bg-neutral-second'} `}>
                                        <div className="flex items-center justify-center">
                                            <Image
                                                src={option.iconUrl}
                                                alt={option.label}
                                                width={20}
                                                height={20}
                                                className="object-contain"
                                            />
                                        </div>
                                    </div>
                                    <span className={`ml-3 text-base font-medium leading-tight ${isActive ? 'font-bold' : ''} max-w-30`}>
                                        {t(option.label)}
                                    </span>
                                </Link>

                                {isActive && option.subOptions && (
                                    <div className="ml-17 pr-4 pb-4 space-y-2">
                                        {option.subOptions.map((sub, index) => (
                                            <Link
                                                key={sub.id}
                                                href={sub.path}
                                                className={`block text-sm transition-colors ${activeOption === sub.id
                                                    ? 'text-neutral-second font-bold'
                                                    : 'text-neutral-first font-medium'
                                                    }`}
                                            >
                                                {t(sub.label)}
                                            </Link>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
