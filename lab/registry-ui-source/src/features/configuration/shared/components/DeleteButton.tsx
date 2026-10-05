'use client';

import Image from 'next/image';

interface Props {
    label: string;
    onClick: (e: React.MouseEvent<HTMLButtonElement>) => void | Promise<void>;
}

export default function DeleteButton({ label, onClick }: Props) {
    return (
        <button
            onClick={async (e) => {
                e.preventDefault();
                e.stopPropagation();
                await onClick(e);
            }}
            className="flex items-center hover:opacity-80 transition-opacity"
            title={label}
        >
            <span className="font-medium text-neutral-first/50">{label}</span>
            <Image
                src="/images/common/false_sign.png"
                alt={label}
                width={18}
                height={18}
                className="ml-2"
            />
        </button>
    );
}