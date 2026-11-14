import { NextRequest } from "next/server";
import { proxyToBackend } from "@/app/api/_lib/backend-proxy";

export async function POST(req: NextRequest) {
    return proxyToBackend({
        req,
        targetEndpoint: '/register-metadata/get_register_schema',
        buildPayload: (body) => ({
            pagination_request: undefined,
            request_payload: {
                register_id: body.register_id,
            },
        }),
        transformResponse: (responseBody) => responseBody.response_payload.filter_schema
    });
}


// Example Result should be
/*
  [
    {
      "field_name": "first_name",
      "display_label": "First Name",
      "filter_type": "text",
      "order": 1,
      "allowed_operators": ["eq", "contains"]
    },
    {
      "field_name": "last_name",
      "display_label": "Last Name",
      "filter_type": "text",
      "order": 2,
      "allowed_operators": ["eq", "contains"]
    },
    {
      "field_name": "gender",
      "display_label": "Gender",
      "filter_type": "dropdown",
      "order": 3,
      "allowed_operators": ["eq", "in"],
      "options_source": [
        { "value": "MALE", "label": "Male" },
        { "value": "FEMALE", "label": "Female" },
        { "value": "OTHER", "label": "Other" }
      ]
    },
    {
      "field_name": "country_code",
      "display_label": "Country Code",
      "filter_type": "dropdown",
      "order": 4,
      "allowed_operators": ["eq", "in"],
      "options_source": [
        { "value": "+1", "label": "United States (+1)" },
        { "value": "+91", "label": "India (+91)" },
        { "value": "+44", "label": "United Kingdom (+44)" },
        { "value": "+61", "label": "Australia (+61)" },
        { "value": "+81", "label": "Japan (+81)" },
        { "value": "+49", "label": "Germany (+49)" },
        { "value": "+33", "label": "France (+33)" },
        { "value": "+86", "label": "China (+86)" },
        { "value": "+971", "label": "UAE (+971)" },
        { "value": "+92", "label": "Pakistan (+92)" }
      ]
    },
    {
      "field_name": "land_size",
      "display_label": "Land Size",
      "filter_type": "number_range",
      "order": 5,
      "allowed_operators": ["eq", "gt", "gte", "lt", "lte", "between"]
    },
    {
      "field_name": "birth_date",
      "display_label": "Birth Date",
      "filter_type": "date_range",
      "order": 6,
      "allowed_operators": ["eq", "gt", "gte", "lt", "lte", "between"]
    },
    {
      "field_name": "is_disabled",
      "display_label": "Disabled",
      "filter_type": "boolean",
      "order": 7,
      "allowed_operators": ["eq"]
    }
  ]
 */
