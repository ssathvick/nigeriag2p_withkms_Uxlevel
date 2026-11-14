import { NextRequest, NextResponse } from 'next/server';
import { getBackendConfig } from '@/app/api/_lib/backend-config';
import { requireAuth } from '@/app/api/_lib/requireAuth';

export async function POST(req: NextRequest) {
    const auth = requireAuth(req);

    if (auth instanceof NextResponse) {
        return auth;
    }

    try {
        const body = await req.json();

        const backendConfig = getBackendConfig();

        const queryParams = new URLSearchParams({
            register_id: body.register_id,
            intake_form_id: body.intake_form_id,
            data_model: body.data_model_mnemonic,
        });

        const response = await fetch(
            `${backendConfig.backendApiUrl}/input-mechanism-data/ingest-data?${queryParams.toString()}`,
            {
                method: 'POST',
                headers: {
                    ...auth.backendHeaders,
                    'Content-Type': 'application/json',
                    accept: 'application/json',
                },
                body: JSON.stringify(body.vc_payload),
            }
        );

        const result = await response.json();

        return NextResponse.json(result, {
            status: response.status,
        });
    } catch (e) {
        return NextResponse.json(
            {
                error:
                    e instanceof Error
                        ? e.message
                        : 'Internal Server Error',
            },
            { status: 500 }
        );
    }
}
