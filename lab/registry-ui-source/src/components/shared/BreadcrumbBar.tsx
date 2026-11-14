"use client";

import Image from "next/image";
import { Link } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';

type BreadcrumbItem = {
    label: string;
    href?: string;
};

interface BreadcrumbBarProps {
    breadcrumb?: BreadcrumbItem[];
}

export default function BreadcrumbBar({ breadcrumb = [] }: BreadcrumbBarProps) {
    const t = useTranslations();
    if (breadcrumb.length === 0) {
        return (
            <div className="flex flex-wrap items-end gap-2">
                <Link href="/" passHref>
                    <div className="h-7.5 flex items-end pb-0.5 pr-2 cursor-pointer">
                        <Image src="/images/common/home.png" width={22} height={22} alt={t('home')} />
                    </div>
                </Link>

                {[1, 2].map(i => (
                    <div key={i} className="flex flex-wrap items-end gap-2">
                        <div className="h-5.75 w-20 rounded bg-secondary-third" />
                        <div className="h-5.75 w-20 rounded bg-secondary-third" />
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="flex flex-wrap items-end gap-2">
            <Link href="/" passHref>
                <div className="h-7.5 flex items-end pb-0.5 pr-2 cursor-pointer">
                    <Image src="/images/common/home.png" width={22} height={22} alt={t('home')} />
                </div>
            </Link>

            {breadcrumb.map((item, index) => {
                const isLast = index === breadcrumb.length - 1;
                const textColor = isLast ? "text-neutral-first" : "text-neutral-first/50";

                return (
                    <div key={index} className="flex flex-wrap items-end gap-2">
                        {/* <div className="h-[23px] flex items-end font-medium text-[20px] text-neutral-first leading-none"> */}
                        <div
                            className={`min-h-5.75 flex items-end font-medium text-[20px] leading-none ${textColor}`}
                        >
                            {item.href && !isLast ? (
                                <Link href={item.href}>{item.label}</Link>
                            ) : (
                                <span>{item.label}</span>
                            )}
                        </div>
                        {!isLast && (
                            <div className="flex items-end pb-1">
                                <Image
                                    src="/images/common/breadcrumb_arrow.png"
                                    width={8}
                                    height={14}
                                    alt={t('arrow')}
                                    className="w-2 3.5"
                                />
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
