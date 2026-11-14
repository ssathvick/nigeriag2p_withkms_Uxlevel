'use client';

import { usePathname } from 'next/navigation';
import { ConfigLayout, type ConfigActiveOption } from '@/features/configuration/shared';
import RequireAction from '@/components/shared/RequireAction';
import {sectionForPath} from '@/features/configuration/shared/components/configurationAccess';

const SIDEBAR_OPTIONS: ConfigActiveOption[] = [
    'registry', 'registry-details', 'registry-themes', 'registry-languages', 'registers',
    'intake-forms', 'data-models', 'ingest-configurations', 'outgest-configurations',
    'ingest-key-paths', 'ingest-semantic-patterns', 'ingest-manage-subscription',
    'ingest-templates', 'outgest-topics', 'outgest-templates', 'data-policies', 'awe-policy-config'
];

function getActiveOptionFromPathname(pathname: string | null): ConfigActiveOption {
    if (!pathname) return 'registry-details';
    const segments = pathname.split('/').filter(Boolean);
    const configIndex = segments.indexOf('configuration');

    if (configIndex === -1 || configIndex === segments.length - 1) return 'registry-details';

    const parentSegment = segments[configIndex + 1];
    const subSegment = segments[configIndex + 2];

    if (subSegment) {
        if (parentSegment === 'registry') {
            if (subSegment === 'details') return 'registry-details';
            if (subSegment === 'themes') return 'registry-themes';
            if (subSegment === 'languages') return 'registry-languages';
        }
        if (parentSegment === 'ingest-configurations') {
            if (subSegment === 'key-paths') return 'ingest-key-paths';
            if (subSegment === 'semantic-patterns') return 'ingest-semantic-patterns';
            if (subSegment === 'manage-subscription') return 'ingest-manage-subscription';
            if (subSegment === 'templates') return 'ingest-templates';
        }
        if (parentSegment === 'outgest-configurations') {
            if (subSegment === 'topics') return 'outgest-topics';
            if (subSegment === 'templates') return 'outgest-templates';
        }
    }

    const option = parentSegment as ConfigActiveOption;
    if (option === 'registry') return 'registry-details';
    return SIDEBAR_OPTIONS.includes(option) ? option : 'registry-details';
}

export default function ConfigurationLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const pathname = usePathname();
    const activeOption = getActiveOptionFromPathname(pathname);

    if (pathname?.endsWith('/configuration/registry/users')) {
        return <RequireAction action="registryConfiguration:edit">{children}</RequireAction>;
    }

    return (
        <RequireAction action={pathname?.endsWith('/new')||pathname?.endsWith('/create')?sectionForPath(pathname||'').access.create:sectionForPath(pathname||'').access.view}>
            <ConfigLayout activeOption={activeOption}>
                {children}
            </ConfigLayout>
        </RequireAction>
    );
}
