'use client';

import Image from 'next/image';

interface Props {
    label: string;
    onClick: () => void;
}

export default function ViewButton({ label, onClick }: Props) {
    return (
        <button
            onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onClick();
            }}
            className="flex items-center hover:opacity-80 transition-opacity"
            title={label}
        >
            <span className="font-medium text-toast-success">{label}</span>
            <Image
                src="/images/common/view.png"
                alt={label}
                width={18}
                height={18}
                className="ml-2"
            />
        </button>
    );
}
