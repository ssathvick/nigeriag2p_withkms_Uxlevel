'use client';

import { useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { Link } from '@/i18n/navigation';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    const t = useTranslations('common');
    const tRoot = useTranslations();

    useEffect(() => {
        console.error("Rendering Error", error);
    }, [error]);

    return (
        <div className="min-h-screen bg-secondary-first">
            {/* Header / Breadcrumb */}
            <div className="w-full h-17.5 flex justify-center items-center">
                <div className="w-full px-7.5 flex justify-between items-center">
                    <div className="flex items-end gap-2">
                        <Link href="/" passHref>
                            <div className="h-7.5 flex items-end pb-0.5 pr-2 cursor-pointer">
                                <Image src="/images/common/home.png" width={22} height={22} alt="home" />
                            </div>
                        </Link>

                        <div className="h-5.75 flex items-end font-medium text-[20px] leading-none">
                            <span>{tRoot("error")}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Card */}
            <div className="flex flex-1 items-center justify-start px-8">
                <div className="w-full bg-neutral-second rounded-[10px] py-36 flex flex-col items-center text-center">
                    <Image
                        src="/images/common/error.png"
                        width={200}
                        height={200}
                        alt="Error illustration"
                        className="mb-6"
                        priority
                    />

                    <h1 className="mb-1 text-[40px] font-semibold leading-11.75 text-primary-second">
                        {t('something_went_wrong')}
                    </h1>

                    <p className="mb-6 text-[20px] font-light leading-6 text-neutral-first/50">
                        {t('something_went_wrong_subtitle')}
                    </p>

                    <button
                        onClick={() => reset()}
                        className="flex items-center justify-center rounded-full bg-neutral-first px-8 py-1.5 text-lg font-medium text-neutral-second transition-all hover:bg-secondary-second-800"
                    >
                        {t('retry')}
                    </button>
                </div>
            </div>
        </div>
    );
}
