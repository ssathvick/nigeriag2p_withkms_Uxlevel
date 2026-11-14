export interface BenefitCode {
    id: number;
    benefit_code_mnemonic: string;
    benefit_type: string;
    benefit_code_description: string;
    benefit_code_max_quantity: number;
}

export interface Program {
    id: number;
    program_mnemonic: string;
    program_description: string;
    enrolment_date?: string;
    am_i_enrolled?: boolean;
    benefit_codes: BenefitCode[];
}
