import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function GET(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/registry-config/get_registry_configuration",
    });
}
