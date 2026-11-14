import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(request: NextRequest) {
    return proxyToBackend({
        req: request,
        targetEndpoint: "/register-section-metadata/create_section",
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                section_register_id: body.section_register_id,
                register_id: body.register_id,
                section_mnemonic: body.section_mnemonic,
                section_description: body.section_description,
                documents_required: body.documents_required || false,
                no_of_verifications_required: body.no_of_verifications_required || 0,
                cr_auto_approve_for_bene_portal: body.cr_auto_approve_for_bene_portal || false,
                cr_auto_approve_for_agent_portal: body.cr_auto_approve_for_agent_portal || false,
                cr_auto_approve_for_staff_portal: body.cr_auto_approve_for_staff_portal || false,
                cr_auto_approve_for_partner: body.cr_auto_approve_for_partner || false,
                is_list: body.is_list || false,
                is_core_section: body.is_core_section || false,
                section_weightage: body.section_weightage || 0,
                section_ui_schema: body.section_ui_schema || {}
            },
        }),
    });
}
