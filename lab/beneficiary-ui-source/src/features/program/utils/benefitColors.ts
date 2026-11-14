export const BENEFIT_COLORS = [
    { bg: "bg-[#E3F9E5]", text: "text-[#1F8A70]" },
    { bg: "bg-[#FFF4E5]", text: "text-[#E67E22]" },
    { bg: "bg-[#E6F2FF]", text: "text-[#2980B9]" },
    { bg: "bg-[#FFF9E5]", text: "text-[#D4A017]" },
    { bg: "bg-[#F3E8FD]", text: "text-[#9B59B6]" },
    { bg: "bg-[#FFE5E5]", text: "text-[#C0392B]" },
    { bg: "bg-[#E5FFE8]", text: "text-[#27AE60]" },
    { bg: "bg-[#E5F7FF]", text: "text-[#3498DB]" },
    { bg: "bg-[#FDEDEC]", text: "text-[#E74C3C]" },
    { bg: "bg-[#F9EBEA]", text: "text-[#8E44AD]" },
    { bg: "bg-[#EAF2F8]", text: "text-[#21618C]" },
    { bg: "bg-[#FEF5E7]", text: "text-[#CA6F1E]" },
    { bg: "bg-[#E8F8F5]", text: "text-[#148F77]" },
    { bg: "bg-[#F6DDCC]", text: "text-[#A04000]" },
    { bg: "bg-[#FDEBD0]", text: "text-[#B9770E]" },
    { bg: "bg-[#E8DAEF]", text: "text-[#7D3C98]" },
    { bg: "bg-[#D6EAF8]", text: "text-[#1B4F72]" },
    { bg: "bg-[#D4EFDF]", text: "text-[#1E8449]" },
    { bg: "bg-[#FADBD8]", text: "text-[#922B21]" },
    { bg: "bg-[#EBDEF0]", text: "text-[#633974]" },
    { bg: "bg-[#D5DBDB]", text: "text-[#424949]" },
    { bg: "bg-[#F2F4F4]", text: "text-[#707B7C]" },
    { bg: "bg-[#FEF9E7]", text: "text-[#A04000]" },
    { bg: "bg-[#E8EAF6]", text: "text-[#283593]" },
];

const benefitColorMap = new Map<string, { bg: string; text: string }>();

export function getColorForBenefit(benefitMnemonic: string) {
    if (!benefitColorMap.has(benefitMnemonic)) {
        const index = benefitColorMap.size % BENEFIT_COLORS.length;
        benefitColorMap.set(benefitMnemonic, BENEFIT_COLORS[index]);
    }
    return benefitColorMap.get(benefitMnemonic)!;
}
