'use client';
import {useConfigurationAccess} from './configurationAccess';
import {useRbac} from '@/context/RbacContext';

import { useTranslations } from "next-intl";

interface Props {
    isActive: boolean;
    onToggle: (e: React.MouseEvent<HTMLButtonElement>) => void | Promise<void>;
    disabled?: boolean;
}

export default function ToggleStatusSwitch({
    isActive,
    onToggle,
    disabled,
}: Props) {
    const t = useTranslations();const access=useConfigurationAccess();const {can}=useRbac();
    if(disabled||(access&&!can(access.edit)))return <span className={'configuration-status'+(isActive?' is-active':'')}>{isActive?'Active':'Inactive'}</span>;
    return (
        <button
            onClick={async (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (disabled) return;
                await onToggle(e);
            }}
            disabled={disabled}
            title={t('toggle_status')}
            className={`relative w-12 h-6 rounded-full transition-colors duration-300 items-center ${isActive ? 'bg-toast-success' : 'bg-secondary-third'} ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
            <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-neutral-second rounded-full shadow-md transform transition-transform duration-300 ${isActive ? 'translate-x-6' : 'translate-x-0'}`}
            />
        </button>
    );
}
