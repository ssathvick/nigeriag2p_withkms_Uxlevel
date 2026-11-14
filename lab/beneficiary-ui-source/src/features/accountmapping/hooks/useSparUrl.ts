"use client";

import { useDepartment } from "@/context/GlobalContext";
import { useRuntimeConfig } from "@/context/RuntimeConfigContext";

export function useSparUrl() {
    const { currentDepartment } = useDepartment();
    const { multiDepartmentEnabled, sparApiUrl } = useRuntimeConfig();

    return multiDepartmentEnabled
        ? currentDepartment?.spar_url ?? ""
        : sparApiUrl;
}
