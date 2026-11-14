export interface Agent {
    name: string;
    address: string
}

export interface Benefit {
    programName: string;
    benefitCode: string;
    quantity: string;
    dateReceived: string;
    agent: Agent;
    deliveryDateTime: string;
    address: string;
    mapImageUrl: string;
    evidenceImages: string[];
    biometricVerified: boolean;
    verificationType: string;
}
