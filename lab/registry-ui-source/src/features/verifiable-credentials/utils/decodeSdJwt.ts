import { decodeSdJwt, getClaims } from "@sd-jwt/decode";
import { digest } from "@sd-jwt/crypto-browser";

export const decodeSdJwtToken = async (sdjwt: string) => {
    const decoded = await decodeSdJwt(sdjwt, digest);

    const disclosedClaims: Record<string, any> = {};

    for (const disclosure of decoded.disclosures) {
        const { key, value } = disclosure as any;
        if (key) disclosedClaims[key] = value;
    }

    const allClaims = await getClaims(
        decoded.jwt.payload,
        decoded.disclosures,
        digest
    );

    if (typeof allClaims !== "object" || allClaims === null) {
        throw new Error("Invalid claims structure");
    }

    const claimsObj = allClaims as Record<string, any>;

    const regularClaims = Object.fromEntries(
        Object.entries(claimsObj).flatMap(([key, value]) => {
            if (disclosedClaims[key]) return [];

            if (
                key === "credentialSubject" &&
                typeof value === "object" &&
                value !== null
            ) {
                return Object.entries(value as Record<string, any>).filter(
                    ([subKey]) => !disclosedClaims[subKey]
                );
            }

            return [[key, value]];
        })
    );

    return {
        decodedJwt: {
            header: decoded.jwt.header,
            payload: decoded.jwt.payload,
            disclosures: decoded.disclosures,
        },
        regularClaims,
        disclosedClaims,
        decoded
    };
};
