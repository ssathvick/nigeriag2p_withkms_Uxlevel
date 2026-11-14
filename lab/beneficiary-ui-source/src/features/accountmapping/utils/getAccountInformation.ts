export async function getAccountInformation() {
    const res = await fetch("/portal/api/account-information", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-cache",
    });

    if (!res.ok) throw new Error("Failed to fetch account information");

    return res.json();
}
