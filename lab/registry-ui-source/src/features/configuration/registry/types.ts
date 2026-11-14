export interface ThemeAttribute {
    theme_value_id: string;
    theme_id: string;
    attribute_name: string;
    attribute_value: string;
}

export interface Theme {
    theme_id: string;
    theme_mnemonic: string;
    is_factory_shipped?: boolean;
}

export interface ThemeAttributeUpdate {
    attribute_name: string;
    attribute_value: string;
}

export const COLOR_ATTRIBUTES = [
    { key: 'primary_color_1', label: 'Primary Color 1', description: 'Main brand color (e.g. yellow)' },
    { key: 'primary_color_2', label: 'Primary Color 2', description: 'Secondary brand color (e.g. orange)' },
    { key: 'secondary_color_1', label: 'Secondary Color 1', description: 'Light background color' },
    { key: 'secondary_color_2', label: 'Secondary Color 2', description: 'Medium gray for borders' },
    { key: 'secondary_color_3', label: 'Secondary Color 3', description: 'Dark gray for muted text' },
    { key: 'neutral_color_1', label: 'Neutral Color 1', description: 'Main text color' },
    { key: 'neutral_color_2', label: 'Neutral Color 2', description: 'Secondary text color' },
] as const;

export const TYPOGRAPHY_ATTRIBUTES = [
    { key: 'font_url', label: 'Font URL', description: 'URL to the font file (e.g. Google Fonts)' },
    { key: 'font_family', label: 'Font Family', description: 'Font family name (e.g. "Inter", sans-serif)' },
] as const;

export const IMAGE_ATTRIBUTES = [
    { key: 'dashboard_image', label: 'Dashboard Image', description: 'Main image displayed on the login/dashboard' },
] as const;

export const THEME_ATTRIBUTES = [...COLOR_ATTRIBUTES, ...TYPOGRAPHY_ATTRIBUTES, ...IMAGE_ATTRIBUTES];

export type ColorAttributeKey = typeof COLOR_ATTRIBUTES[number]['key'];
export type ThemeAttributeKey = typeof THEME_ATTRIBUTES[number]['key'];

export interface Language {
    language_id: string;
    language_code: string;
    language_label: string;
    language_flag_base64: string;
    is_default: boolean;
    language_translation: Record<string, any>;
}
