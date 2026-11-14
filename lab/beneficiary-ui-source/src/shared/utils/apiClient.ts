const BASE_PATH = "/portal";

export async function portalApi<T = any>(
    endpoint: string,
    body: object = {},
    headers: Record<string, string> = {}
): Promise<T> {
    const finalHeaders: Record<string, string> = {
        "Content-Type": "application/json",
        ...headers,
    };

    const response = await fetch(`${BASE_PATH}${endpoint}`, {
        method: "POST",
        credentials: "include",
        headers: finalHeaders,
        body: JSON.stringify(body),
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        throw new Error(data?.error || "Portal operation failed");
    }

    return data;
}
