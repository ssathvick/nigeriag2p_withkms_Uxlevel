import 'server-only';
import { z } from 'zod';
import { ImportError } from './native';
import { limits } from './model';

const connectorSpec = z.record(z.string().regex(/^[a-z0-9_-]{1,50}$/), z.object({
    label: z.string().min(1).max(100),
    url: z.url(),
    tokenEnv: z.string().regex(/^DATA_IMPORTS_CONNECTOR_[A-Z0-9_]+_TOKEN$/).optional(),
}));

function configured() {
    if (!process.env.DATA_IMPORTS_CONNECTORS) return {};
    return connectorSpec.parse(JSON.parse(process.env.DATA_IMPORTS_CONNECTORS));
}

export function connectorChoices() {
    return Object.entries(configured()).map(([id, entry]) => ({ id, label: entry.label }));
}

export async function fetchSourceFile(connectorId: string) {
    const connectors = configured();
    const connector = Object.hasOwn(connectors, connectorId) ? connectors[connectorId] : undefined;
    if (!connector) throw new ImportError('This source connection is unavailable.', 422);
    const url = new URL(connector.url);
    const local = process.env.DATA_IMPORTS_LOCAL_PREVIEW === '1' && url.origin === 'http://127.0.0.1:3101';
    if ((url.protocol !== 'https:' && !local) || url.username || url.password) {
        throw new ImportError('The source connection requires a valid HTTPS endpoint.', 503);
    }
    const token = connector.tokenEnv ? process.env[connector.tokenEnv] : undefined;
    if (connector.tokenEnv && !token) throw new ImportError('The source connection is missing its server credential.', 503);
    const headers = new Headers({ Accept: 'text/csv' });
    if (token) headers.set('Authorization', `Bearer ${token}`);
    try {
        const response = await fetch(url, {
            headers, redirect: 'error', cache: 'no-store', signal: AbortSignal.timeout(15000),
        });
        if (!response.ok || !response.body || !response.headers.get('content-type')?.toLowerCase().startsWith('text/csv')) throw new Error();
        const parts: Uint8Array[] = [];
        let length = 0;
        for await (const part of response.body as unknown as AsyncIterable<Uint8Array>) {
            length += part.byteLength;
            if (length > limits.file) throw new ImportError('The connected source returned a file larger than 2 MB.', 413);
            parts.push(part);
        }
        return new File([Buffer.concat(parts)], `${connectorId}.csv`, { type: 'text/csv' });
    } catch (error) {
        if (error instanceof ImportError) throw error;
        throw new ImportError('The source API did not return a CSV file. Try again or contact the source administrator.', 502);
    }
}
