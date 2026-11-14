"use client";

import { useDepartment } from "@/context/GlobalContext";
import { useRuntimeConfig } from "@/context/RuntimeConfigContext";

export function useBridgeUrl() {
    const { currentDepartment } = useDepartment();
    const { multiDepartmentEnabled, bridgeApiUrl } = useRuntimeConfig();

    return multiDepartmentEnabled
        ? currentDepartment?.bridge_url ?? ""
        : bridgeApiUrl;
}
