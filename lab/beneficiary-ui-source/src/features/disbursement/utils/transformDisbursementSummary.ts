import {
    DisbursementItem,
    DisbursementSummary
} from "@/features/disbursement/types/disbursementTypes";

export function transformDisbursementSummary(list: DisbursementItem[] = []): DisbursementSummary {
    return {
        digital_cash: list
            .filter(i => i.benefit_type === "CASH_DIGITAL")
            .reduce((sum, i) => sum + (i.total_quantity_received ?? 0), 0),

        physical_cash: list
            .filter(i => i.benefit_type === "CASH_PHYSICAL")
            .reduce((sum, i) => sum + (i.total_quantity_received ?? 0), 0),

        commodity: list
            .filter(i => i.benefit_type === "COMMODITY")
            .reduce((sum, i) => sum + (i.total_quantity_received ?? 0), 0),

        service: list
            .filter(i => i.benefit_type === "SERVICE")
            .reduce((sum, i) => sum + (i.total_quantity_received ?? 0), 0),
    };
}
