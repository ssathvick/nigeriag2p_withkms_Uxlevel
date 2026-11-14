export type Branding = {
    primary_color_1?: string;
    primary_color_2?: string;
    secondary_color_1?: string;
    secondary_color_2?: string;
    secondary_color_3?: string;
    neutral_color_1?: string;
    neutral_color_2?: string;
    font_url?: string;
    font_family?: string;
    dashboard_image?: string;
    toast_color?: {
        toast_info_color?: string;
        toast_success_color?: string;
        toast_warning_color?: string;
        toast_failed_color?: string;
    }
};
export type LanguageConfig = {
    language_id: string;
    language_code: string;
    language_label: string;
    language_flag_base64: string;
    is_default: boolean;
    language_translation: Record<string, any>;
};
export type ClientSafeConfigShape = {
    partnerImportExportEnable: boolean;
    verifyServiceUrl: string;
    vpClientId: string;
    pageSize: number;
    registryName: string;
    registryLogo: string;
    registry_theme_id: string;
    registry_language_id: string;
    branding?: Branding;
    language_config?: LanguageConfig;
};
