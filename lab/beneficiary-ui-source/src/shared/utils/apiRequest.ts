export async function apiRequest(
    baseUrl: string,
    endpoint: string,
    body: object = {},
    headers: Record<string, string> = {}
) {
    const cookieToken = document?.cookie
        ?.split("; ")
        ?.find(row => row.startsWith("X-Access-Token="))
        ?.split("=")[1];

    const finalHeaders: Record<string, string> = {
        "Content-Type": "application/json",
        ...headers,
    };

    if (cookieToken) {
        finalHeaders["Authorization"] = `Bearer ${cookieToken}`;
    }

    const response = await fetch(`${baseUrl}${endpoint}`, {
        method: "POST",
        credentials: "include",
        headers: finalHeaders,
        body: JSON.stringify(body),
    });

    const data = await response.json().catch(() => null);
    return data;
}
