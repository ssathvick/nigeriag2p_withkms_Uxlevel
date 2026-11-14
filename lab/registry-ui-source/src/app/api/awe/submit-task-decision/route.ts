import { NextRequest } from 'next/server';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: '/awe/submit_task_decision',
        buildPayload: (body) => ({
            request_payload: {
                task_id: body.task_id,
                action: body.action,
                comment: body.comment ?? null,
                attachments_ref: body.attachments_ref ?? null,
                artifact_id: body.artifact_id,
                artifact_type: body.artifact_type,
                current_stage: body.current_stage,
            },
        }),
        transformResponse: (responseBody) => ({
            decision: responseBody?.response_payload?.data,
        }),
    });
}
