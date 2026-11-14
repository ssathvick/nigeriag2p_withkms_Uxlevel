'use client';
import {useConfigurationAccess} from './configurationAccess';
import {useRbac} from '@/context/RbacContext';

import { Pencil } from 'lucide-react';

interface Props {
    label: string;
    onClick: () => void;
}

export default function EditButton({ label, onClick }: Props) {
    const access=useConfigurationAccess();const {can}=useRbac();
    if(access&&!can(access.edit))return null;
    return (
        <button
            onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onClick();
            }}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            title={label}
        >
            <span className="font-medium text-neutral-first/50">{label}</span>
            <Pencil size={16} className="opacity-60" />
        </button>
    );
}
