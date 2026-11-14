export interface DisbursementItem {
    benefit_code_mnemonic: string;
    benefit_type: "CASH_DIGITAL" | "CASH_PHYSICAL" | "COMMODITY" | "SERVICE";
    measurement_unit: string;
    total_quantity_received: number;
}

export interface DisbursementSummary {
    digital_cash: number;
    physical_cash: number;
    commodity: number;
    service: number;
}

export interface BenefitCardData {
    icon: string;
    value: number;
    label: string;
}

export interface DisbursementRecord {
    agency_mnemonic: string;
    benefit_code: string;
    benefit_type: "CASH_DIGITAL" | "CASH_PHYSICAL" | "COMMODITY" | "SERVICE";
    cycle_code_mnemonic: string;
    disbursement_envelope_id: string;
    disbursement_id: string;
    disbursement_quantity: number;
    disbursement_schedule_date: string;
    measurement_unit: string;
    program_mnemonic: string;
}
