import "server-only";

//backend configuration (use in API routes)
export function getBackendConfig() {
    return {
        backendApiUrl: process.env.BACKEND_API_URL ?? "",
        masterdataBackendApiUrl: process.env.MASTERDATA_BACKEND_API_URL ?? "",
        iamUrl: process.env.IAM_URL ?? "",
        keycloakLogoutUrl: process.env.KEYCLOAK_LOGOUT_URL ?? "",
        loginProviderId: process.env.LOGIN_PROVIDER_ID ?? "",
        applicationMnemonic: process.env.APPLICATION_MNEMONIC ?? "openg2p-registry",
        cookieDomain: process.env.COOKIE_DOMAIN ?? "",
        redirectUrl: process.env.REDIRECT_URL
    };
}
