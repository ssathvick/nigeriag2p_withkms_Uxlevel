'use client';

import Image from 'next/image';
import { Link } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';

export default function Forbidden() {
    const t = useTranslations();

    return (
        <div className="min-h-screen bg-secondary-first">
            <div className="w-full h-17.5 flex justify-center items-center">
                <div className="w-full px-7.5 flex justify-between items-center">
                    <div className="flex items-end gap-2">
                        <Link href="/" passHref>
                            <div className="h-7.5 flex items-end pb-0.5 pr-2 cursor-pointer">
                                <Image src="/images/common/home.png" width={22} height={22} alt="home" />
                            </div>
                        </Link>

                        <div className="h-5.75 flex items-end font-medium text-[20px] leading-none">
                            <span>403</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex flex-1 items-center justify-start px-7.5">
                <div className="w-full bg-neutral-second rounded-[10px] py-36 flex flex-col items-center text-center">
                    <Image
                        src="/images/common/forbidden.png"
                        width={140}
                        height={140}
                        alt="Forbidden illustration"
                        className="mb-6"
                        priority
                    />

                    <h1 className="mb-4 text-[40px] font-semibold leading-11.75 text-primary-second">
                        {t('access_denied')}
                    </h1>

                    <p className="mb-6 text-[20px] font-light leading-6 text-neutral-first/50 max-w-xl">
                        {t('forbidden_subtitle')}
                    </p>

                    <Link href="/">
                        <button
                            className="flex items-center gap-3 rounded-full bg-neutral-first px-6 py-2.5 text-[16px] font-semibold text-neutral-second"
                        >
                            <Image
                                src="/images/common/left_white_arrow.png"
                                width={16}
                                height={14}
                                alt="left arrow"
                                priority
                            />
                            {t('go_back')}
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    );
}