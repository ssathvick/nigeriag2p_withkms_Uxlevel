export type RuntimeConfig = {
    multiDepartmentEnabled: boolean;

    strapiApiUrl: string;

    pbmsApiUrl: string;
    sparApiUrl: string;
    bridgeApiUrl: string;

    novu: {
        applicationIdentifier: string;
        backendUrl: string;
        socketUrl: string;
    };
};

export function loadRuntimeConfig(): RuntimeConfig {
    return {
        multiDepartmentEnabled: process.env.MULTI_DEPARTMENT_ENABLED === "true",

        strapiApiUrl: process.env.STRAPI_API_URL ?? "",

        pbmsApiUrl: process.env.PBMS_API_URL ?? "",
        sparApiUrl: process.env.SPAR_API_URL ?? "",
        bridgeApiUrl: process.env.BRIDGE_API_URL ?? "",

        novu: {
            applicationIdentifier: process.env.NOVU_APPLICATION_IDENTIFIER ?? "",
            backendUrl: process.env.NOVU_BACKEND_URL ?? "",
            socketUrl: process.env.NOVU_SOCKET_URL ?? "",
        },
    };
}
