
import "server-only";
import { randomUUID } from "crypto";
import { BackendRequest, RequestBody, RequestHeader } from "./backend-types";

export function generateRequestId(): string {
    return randomUUID();
}

export function generateTimestamp(): string {
    return new Date().toISOString();
}

export function createBackendRequest(payload: RequestBody, origin: string): BackendRequest {
    const requestHeader: RequestHeader = {
        sender_app_mnemonic: "Registry Staff Portal UI",
        sender_app_url: origin,
        request_id: generateRequestId(),
        request_timestamp: generateTimestamp(),
    };

    const requestBody: RequestBody = payload;

    return {
        request_header: requestHeader,
        request_body: requestBody,
    };
}
