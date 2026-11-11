// Presentation labels only: stored identifiers and workflow references stay intact.
export const programmeNames = {
 NG_LAB_HOUSEHOLD: 'Household Support — Demo',
 NG_LAB_FARMER: 'Farmer Support — Demo',
 'IQS-SYN-20261003-HOUSEHOLD': 'Household Cash Support — Synthetic Demo',
 'IQS-SYN-20261003-FARM': 'Smallholder Farming Grant — Synthetic Demo',
 'IQS-SYN-20261003-SCHOOL': 'School Materials Support — Synthetic Demo',
 'IQS-SYN-20261003-LIVELIHOOD': 'Livelihood Starter Grant — Synthetic Demo',
 'IQS-SYN-20261003-RELIEF': 'Emergency Relief Assistance — Synthetic Demo',
 IQS_INTEGRATED_HOUSEHOLD_SUPPORT: 'Household Support — Integrated Demo',
 IQS_INTEGRATED_PORTAL_INGESTION_TEST: 'Beneficiary Portal Application — Integration Test',
 IQS_INTEGRATED_JOS_CCT_DEMO: 'Jos Conditional Cash Transfer — Bank Simulator Demo',
 REACT_UAT_1794293158_0: 'Farmer Benefit Workflow — Acceptance Test 1',
 REACT_UAT_1794293158_1: 'Farmer Benefit Workflow — Acceptance Test 2',
};
export const programmeName = value => programmeNames[value] || (typeof value === 'string' ? value.replace(/_/g, ' ') : value);
export const matchingProgrammeCodes = query => Object.entries(programmeNames).filter(([,name])=>name.toLowerCase().includes(query.toLowerCase())).map(([code])=>code);
