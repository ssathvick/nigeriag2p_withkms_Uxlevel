import "server-only";
import { getBackendConfig } from "./backend-config";
import { createBackendRequest } from "./backend-request";
import { requireAuthFromCookies } from "./requireAuth";

import { Branding, ClientSafeConfigShape, LanguageConfig } from "./client-safe-config.types";

class ClientSafeConfig {
    private config: ClientSafeConfigShape;

    constructor() {
        this.config = {
            partnerImportExportEnable: process.env.PARTNER_IMPORT_EXPORT_ENABLE === "true",
            verifyServiceUrl: process.env.VERIFY_SERVICE_URL ?? "",
            vpClientId: process.env.VP_CLIENT_ID ?? "",
            pageSize: parseInt(process.env.PAGE_SIZE ?? "10"),
            registryName: "",
            registryLogo: "",
            registry_theme_id: "",
            registry_language_id: "",
            branding: {},
        };
    }

    async fetchLanguageConfigByCode(language_code: string, origin: string): Promise<LanguageConfig | undefined> {
        const backendConfig = getBackendConfig();
        const auth = await requireAuthFromCookies();
        if (!auth) return undefined;

        const languagesUrl = `${backendConfig.backendApiUrl}/registry-language/get_all_languages`;
        const languagesRequest = createBackendRequest({
            request_payload: {},
            pagination_request: { current_page: 1, page_size: 100 }
        }, origin);

        try {
            const response = await fetch(languagesUrl, {
                method: "POST",
                headers: {
                    ...auth.backendHeaders,
                },
                body: JSON.stringify(languagesRequest),
                next: {
                    revalidate: 0,
                    tags: ['languages-config']
                }
            });

            if (response.ok) {
                const data = await response.json();
                const languages: LanguageConfig[] = data.response_body?.response_payload || [];
                return languages.find(l => l.language_code === language_code);
            }
        } catch (error) {
            console.error(`Failed to fetch language config for ${language_code}:`, error);
        }
        return undefined;
    }

    async fetchRegistryConfig(origin: string): Promise<ClientSafeConfigShape> {

        const backendConfig = getBackendConfig();
        const backendUrl = `${backendConfig.backendApiUrl}/registry-config/get_registry_configuration`;

        try {
            const auth = await requireAuthFromCookies();
            if (!auth) return this.config;

            const backendRequest = createBackendRequest({ request_payload: {} }, origin);

            const response = await fetch(backendUrl, {
                method: "POST",
                headers: {
                    ...auth.backendHeaders,
                },
                body: JSON.stringify(backendRequest),
                next: {
                    revalidate: 0,
                    tags: ['registry-config']
                }
            });

            if (response.ok) {
                const data = await response.json();
                const rawPayload = data.response_body?.response_payload;
                const payload = Array.isArray(rawPayload) ? rawPayload[0] : rawPayload;
                const theme_id = payload?.registry_theme_id;

                let branding: Branding = {};

                if (theme_id) {
                    const themeUrl = `${backendConfig.backendApiUrl}/registry-theme/get_theme_values`;
                    const themeRequest = createBackendRequest({
                        request_payload: { theme_id: theme_id }
                    }, origin);

                    const themeResponse = await fetch(themeUrl, {
                        method: "POST",
                        headers: {
                            ...auth.backendHeaders,
                        },
                        body: JSON.stringify(themeRequest),
                        next: {
                            revalidate: 0,
                            tags: ['theme-config']
                        }
                    });

                    if (themeResponse.ok) {
                        const themeData = await themeResponse.json();
                        const attributes = themeData.response_body?.response_payload || [];

                        attributes.forEach((attr: { attribute_name: string; attribute_value: string }) => {
                            (branding as any)[attr.attribute_name] = attr.attribute_value;
                        });
                    }
                }

                const language_id = payload?.registry_language_id;
                let language_config: LanguageConfig | undefined = undefined;

                if (language_id) {
                    const languageUrl = `${backendConfig.backendApiUrl}/registry-language/get_language`;
                    const languageRequest = createBackendRequest({
                        request_payload: { language_id: language_id }
                    }, origin);

                    const languageResponse = await fetch(languageUrl, {
                        method: "POST",
                        headers: {
                            ...auth.backendHeaders,
                        },
                        body: JSON.stringify(languageRequest),
                        next: {
                            revalidate: 0,
                            tags: ['language-config']
                        }
                    });

                    if (languageResponse.ok) {
                        const languageData = await languageResponse.json();
                        language_config = languageData.response_body?.response_payload;
                    }
                }
                this.setMany({
                    registryName: payload?.registry_name ?? "",
                    registryLogo: payload?.registry_logo ?? "",
                    registry_theme_id: theme_id ?? "",
                    registry_language_id: language_id ?? "",
                    branding,
                    language_config,
                });
            }
        } catch (error) {
            console.error("Failed to fetch registry config:", error);
        }
        return this.config;
    }

    getAll(): ClientSafeConfigShape {
        return this.config;
    }

    setMany(values: Partial<ClientSafeConfigShape>) {
        this.config = {
            ...this.config,
            ...values,
        };
    }
}

export const clientSafeConfig = new ClientSafeConfig();
