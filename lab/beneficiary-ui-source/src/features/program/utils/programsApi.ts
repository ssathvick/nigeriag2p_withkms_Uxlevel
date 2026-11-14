import { apiRequest } from "@/shared/utils/apiRequest";
import { buildStandardPayload, PaginationParams } from "@/shared/utils/payloadBuilder";

export function getAllPrograms(baseUrl: string, params: PaginationParams = {}) {
    return apiRequest(
        baseUrl,
        "/benefit_program/get_all_programs",
        buildStandardPayload(params)
    );
}

export function getMyPrograms(baseUrl: string, params: PaginationParams = {}) {
    return apiRequest(
        baseUrl,
        "/benefit_program/get_my_programs",
        buildStandardPayload(params)
    );
}

export function getProgramById(baseUrl: string, programId: string) {
    return apiRequest(
        baseUrl,
        "/benefit_program/get_program",
        buildStandardPayload({
            extraPayload: { program_id: programId }
        })
    );
}
