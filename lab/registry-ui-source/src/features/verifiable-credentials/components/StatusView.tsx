'use client';

import Image from 'next/image';
import { useTranslations } from 'next-intl';

interface StatusViewProps {
    vp: any;
}

export default function StatusView({ vp }: StatusViewProps) {
    const t = useTranslations();
    const payload = vp?.decodedJwt?.payload;
    const status = vp?.vcStatus;
    const isSuccess = status === 'SUCCESS';
    return (
        <div className="flex-1">
            <div className="grid grid-cols-3 gap-6 min-h-60">
                <div className="bg-secondary-first p-10 flex flex-col justify-center items-center text-center">
                    <p className="text-[16px] text-neutral-first/50 mb-2">{t('credential_type')}</p>
                    <p className="text-[16px] font-semibold">
                        {payload?.vct ?? '—'}
                    </p>
                </div>

                <div className="bg-secondary-first p-10 flex flex-col justify-center items-center text-center">
                    <p className="text-[16px] text-neutral-first/50 mb-2">{t('credential_id')}</p>
                    <p className="text-[16px] font-semibold">
                        {payload?.id ?? '—'}
                    </p>
                </div>

                <div className="bg-secondary-first p-10 flex flex-col justify-center items-center text-center">
                    <Image
                        src={isSuccess ? '/images/common/verified.png' : '/images/common/invalid.png'}
                        alt={status}
                        width={48}
                        height={48}
                        className={`mb-2 p-1 rounded-full ${isSuccess ? '' : 'bg-red-500'}`}
                    />

                    <p className="text-[16px] text-neutral-first/50 mb-2">{t('verification_result')}</p>
                    <p
                        className={`text-[16px] font-semibold ${isSuccess ? 'text-toast-success' : 'text-red-600'}`}
                    >
                        {status}
                    </p>
                </div>
            </div>
        </div>
    );
}
