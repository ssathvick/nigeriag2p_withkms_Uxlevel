'use client';

import Image from 'next/image';
import Link from 'next/link';
import { registryDisplayText } from '@/shared/utils/registryDisplayText';

export type KeyValueVariant = 'split' | 'deduplication' | 'message';

export interface KeyValueProps {
    label: string;
    value: string;
    href?: string;
    valueClassName?: string;
    variant?: KeyValueVariant;
    className?: string;
}

/**
 * Label/value row used across cards (submissions, change requests, messages, deduplication).
 */
export function KeyValue({
    label,
    value,
    href,
    valueClassName,
    variant = 'split',
    className = '',
}: KeyValueProps) {
    const root = className.trim();
    label = registryDisplayText(String(label??''));
    value = registryDisplayText(String(value??'Not recorded'));

    if (variant === 'deduplication') {
        return (
            <div
                className={`application-key-value flex w-full overflow-hidden font-normal leading-[26px] text-neutral-first${root ? ` ${root}` : ''}`}
            >
                <span className="w-1/2 truncate text-[16px] text-neutral-first/50" title={label}>
                    {label} :{' '}
                </span>
                <span
                    className="w-1/2 truncate pl-4 text-[16px] font-normal text-neutral-first"
                    title={value}
                >
                    {value}
                </span>
            </div>
        );
    }

    if (variant === 'message') {
        return (
            <div className={`application-key-value text-neutral-first${root ? ` ${root}` : ''}`}>
                <span className="text-[16px] text-neutral-first/50">{label}: </span>
                <span className={`text-[14px] font-medium ${valueClassName ?? 'text-neutral-first'}`}>{value}</span>
            </div>
        );
    }

    return (
        <div
            className={`application-key-value flex w-full overflow-hidden leading-relaxed text-neutral-first${root ? ` ${root}` : ''}`}
        >
            <span
                className="w-1/2 min-w-0 truncate text-[16px] font-normal text-neutral-first/50"
                title={label}
            >
                {label}:{' '}
            </span>
            <span className={`w-1/2 min-w-0 truncate text-[14px] font-medium ${valueClassName ?? ''}`}>
                {href ? (
                    <Link
                        href={href}
                        className="inline-flex max-w-full items-center truncate text-neutral-first"
                        title={value}
                    >
                        <span className="truncate">{value}</span>
                        <Image
                            src="/images/common/arrow_next_01.png"
                            alt=""
                            width={14}
                            height={14}
                            className="ml-1 inline-block shrink-0"
                        />
                    </Link>
                ) : (
                    <span className="truncate text-neutral-first" title={value}>
                        {value}
                    </span>
                )}
            </span>
        </div>
    );
}
