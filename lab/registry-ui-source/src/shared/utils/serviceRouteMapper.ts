import { transformEndpointName } from './endpointMapper';

/**
 * Maps service and endpoint to Next.js API route URL
 *
 * @param service - Service mnemonic (e.g., "master-data")
 * @param endpoint - Endpoint name (e.g., "get_g2p_geo_level_values")
 * @returns Next.js API route URL (e.g., "/api/master-data/geo-level-values")
 */
export function routeServiceEndpoint(service: string, endpoint: string): string {
    const transformedEndpoint = transformEndpointName(endpoint);
    return `/api/${service}/${transformedEndpoint}`;
}
