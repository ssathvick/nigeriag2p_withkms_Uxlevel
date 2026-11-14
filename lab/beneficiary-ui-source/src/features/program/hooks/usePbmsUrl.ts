"use client";

import { useDepartment } from "@/context/GlobalContext";
import { useRuntimeConfig } from "@/context/RuntimeConfigContext";

export function usePbmsUrl() {
    const { currentDepartment } = useDepartment();
    const { multiDepartmentEnabled, pbmsApiUrl } = useRuntimeConfig();

    return multiDepartmentEnabled
        ? currentDepartment?.pbms_url ?? ""
        : pbmsApiUrl;
}
