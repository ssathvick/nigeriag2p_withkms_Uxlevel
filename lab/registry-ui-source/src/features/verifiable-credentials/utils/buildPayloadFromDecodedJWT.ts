export const buildPayloadFromDecodedJWT = (
    decodedSdJwt: any,
    regularClaims: Record<string, any>,
    disclosedClaims: Record<string, any>
) => {
    // Extract JWT header and payload
    const jwtHeader = decodedSdJwt.header;
    const jwtPayload = decodedSdJwt.payload;


    // Combine regular and disclosed claims for credential_subject
    const credentialSubject = {
        ...regularClaims.credential_subject,
        ...disclosedClaims
    };

    return {
        signature: `Signature: namespace="spdci", kidId="${jwtHeader.kid}", algorithm="${jwtHeader.alg}", created="${Math.floor(Date.now() / 1000)}", expires="${Math.floor(Date.now() / 1000) + 86400}", headers="(created) (expires) digest", signature="${decodedSdJwt.signature || 'Base64(signing content)'}"`,
        header: {
            version: "1.0.0",
            message_id: crypto.randomUUID(),
            message_ts: new Date().toISOString(),
            action: "on-search",
            status: "rcvd",
            sender_id: "civilregistry.example.org",
            receiver_id: "registry.example.org",
            is_msg_encrypted: false,
            meta: {}
        },
        message: {
            // Standard JWT claims
            iss: jwtPayload.iss,
            sub: jwtPayload.sub || jwtPayload.id,
            jti: jwtPayload.id,
            iat: jwtPayload.iat,
            nbf: jwtPayload.nbf,
            exp: jwtPayload.exp,
            vct: jwtPayload.vct,

            // Confirmation claim
            cnf: jwtPayload.cnf,

            // SD-JWT specific
            _sd_alg: jwtPayload._sd_alg,
            _sd: jwtPayload._sd,

            // Credential subject with all disclosed claims
            credential_subject: {
                id: credentialSubject.id || regularClaims.sub,
                given_name: disclosedClaims.given_name || credentialSubject.given_name,
                family_name: disclosedClaims.family_name || credentialSubject.family_name,
                birthdate: disclosedClaims.birthdate || credentialSubject.birth_date,
                place_of_birth: disclosedClaims.place_of_birth || credentialSubject.birth_place,
                // Add other fields as needed
                ...credentialSubject
            },

            // Optional fields from your schema
            event_context: regularClaims.event_context,
            registration: regularClaims.registration,
            certificate: regularClaims.certificate,
            localization: regularClaims.localization,
            derived: regularClaims.derived,

            // Credential status
            credential_status: jwtPayload.credential_status
        }
    };
};
