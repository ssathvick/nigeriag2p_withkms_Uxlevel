import qs from "qs";

export async function strapiServerFetch<T = unknown>(
    path: string,
    qsParams?: Record<string, unknown>
): Promise<T> {
    const baseUrl = process.env.STRAPI_API_URL ?? "http://localhost:1337";
    const url = new URL(path, baseUrl);

    if (qsParams) {
        url.search = qs.stringify(qsParams, { encodeValuesOnly: true });
    }

    const res = await fetch(url.toString(), {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
        throw new Error(data?.error?.message ?? "Strapi fetch failed");
    }

    return data as T;
}
