/**
 * Transforms endpoint names from widget format to API route format
 *
 * Examples:
 * - "get_g2p_geo_level_values" -> "geo_level_values"
 * - "get_g2p_geo_levels" -> "geo_levels"
 * - "get_all_partners" -> "all_partners"
 *
 * Note: Keeps snake_case format to match existing API route naming convention
 */
export function transformEndpointName(endpoint: string): string {
    // Remove common prefixes like "get_", "post_", "put_", "delete_"
    let transformed = endpoint.replace(/^(get_|post_|put_|delete_|patch_)/i, '');

    // Remove "g2p_" prefix if present
    transformed = transformed.replace(/^g2p_/, '');

    // New routes use hyphen-case: geo-level-values, geo-levels
    return transformed.replaceAll('_', '-');
}
