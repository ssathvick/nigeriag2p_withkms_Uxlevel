'use client';

import { Link, useRouter } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import Image from 'next/image';

export default function NotFound() {
    const router = useRouter();
    const t = useTranslations('common');

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
                            <span>{"404"}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex flex-1 items-center justify-start px-8">
                <div className="w-full bg-neutral-second rounded-[10px] py-36 flex flex-col items-center text-center">
                    <Image
                        src="/images/common/404.png"
                        width={200}
                        height={200}
                        alt="404 error illustration"
                        className="mb-6"
                        priority
                    />

                    <h1 className="mb-2 text-4xl font-bold text-primary-second">
                        {t('error_404_title')}
                    </h1>

                    <p className="mb-8 text-lg text-secondary-third">
                        {t('error_404_subtitle')}
                    </p>

                    <button
                        onClick={() => router.back()}
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
                </div>
            </div>
        </div >
    );
}
