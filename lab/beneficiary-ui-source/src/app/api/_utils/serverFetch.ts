import { cookies } from "next/headers";

export async function serverFetch(
    baseUrl: string,
    endpoint: string,
    body: any
) {
    const cookieStore = await cookies();
    const token = cookieStore.get("X-Access-Token")?.value;

    const response = await fetch(`${baseUrl}${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(body),
        cache: "no-store",
    },
    );

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        throw new Error(data?.message || "Mapper API failed");
    }

    return data;
}
