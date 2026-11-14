import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';
import { clientSafeConfig } from '@/app/api/_lib/client-safe-config';
import { getOrigin } from '@/app/api/_lib/get-origin';

export default getRequestConfig(async ({ requestLocale }) => {
    let locale = await requestLocale;

    if (!locale || !routing.locales.includes(locale as any)) {
        locale = routing.defaultLocale;
    }

    //load dynamic messages
    const origin = await getOrigin();
    await clientSafeConfig.fetchRegistryConfig(origin);
    const config = clientSafeConfig.getAll();

    const staticMessagesMap: Record<string, () => Promise<any>> = {
        en: () => import('../../locales/en.json'),
        es: () => import('../../locales/es.json'),
        fr: () => import('../../locales/fr.json'),
    };

    let staticMessages: Record<string, string> = {};
    if (staticMessagesMap[locale as string]) {
        try {
            staticMessages = (await staticMessagesMap[locale as string]()).default;
        } catch {
            // If static file is missing, continue with dynamic translations only
        }
    }

    let dynamicMessages: Record<string, string> = {};
    if (config.language_config?.language_code === locale) {
        dynamicMessages = config.language_config?.language_translation || {};
    } else {
        const dynamicLang = await clientSafeConfig.fetchLanguageConfigByCode(locale as string, origin);
        if (dynamicLang) {
            dynamicMessages = dynamicLang.language_translation || {};
        }
    }

    const messages = { ...staticMessages, ...dynamicMessages };

    return {
        locale,
        messages,
    };
});
