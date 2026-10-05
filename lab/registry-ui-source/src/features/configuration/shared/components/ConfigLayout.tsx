'use client';

import ConfigSidebar from './ConfigSidebar';
import { ReactNode } from 'react';

export type ConfigActiveOption =
    | "registry"
    | "registry-details"
    | "registry-themes"
    | "registry-languages"
    | "registers"
    | "intake-forms"
    | "data-models"
    | "ingest-configurations"
    | "outgest-configurations"
    | "ingest-key-paths"
    | "ingest-semantic-patterns"
    | "ingest-manage-subscription"
    | "ingest-templates"
    | "outgest-topics"
    | "outgest-templates"
    | "data-policies"
    | "awe-policy-config"

interface ConfigLayoutProps {
    children: ReactNode;
    activeOption: ConfigActiveOption;
}

export const ConfigLayout = ({ children, activeOption }: ConfigLayoutProps) => {
    return (
        <div className="min-h-screen mx-auto bg-secondary-first flex">
            <div className="mt-4">
                <ConfigSidebar activeOption={activeOption} />
            </div>
            <div className="flex-1 flex flex-col">
                {children}
            </div>
        </div>
    );
};

export default ConfigLayout;
