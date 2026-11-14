"use client";

import Image from "next/image";
import {useRbac} from '@/context/RbacContext';
import {configurationSections} from '@/features/configuration/shared/components/configurationAccess';
import { useRouter } from "@/i18n/navigation";
import { useTranslations } from 'next-intl';

export default function ConfigurationButton() {
    const router = useRouter();
    const t = useTranslations();const {can}=useRbac();const target=configurationSections.find(s=>can(s.access.view));
    if(!target)return null;

    const goToConfig = () => {
        if(target)router.push(target.path);
    };

    return (
        <button
            aria-label="Configuration"
            onClick={goToConfig}
            className="flex items-center gap-2 hover:opacity-80"
        >
            <Image
                src="/images/config/config_icon.png"
                alt="Config Icon"
                width={24}
                height={24}
            />
            <span className="hidden sm:inline text-[16px] text-neutral-first">
                {t('configuration')}
            </span>
        </button>
    );
}
