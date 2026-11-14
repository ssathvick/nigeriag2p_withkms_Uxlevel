import { useFetch } from "@/shared/hooks/useFetch";
import { ChangeRequest } from "@/features/change-request/types/change-request";
export const useChangeRequest = (changeId: string) => {
    const { data, loading } = useFetch<any>({
        url: `/api/change-request/get`,
        enabled: !!changeId,
        options: {
            method: "POST",
            body: JSON.stringify({ change_request_id: changeId }),
        },
    });

    const details: ChangeRequest | null = data;

    return { details, loading: !!changeId ? loading : false };
};
