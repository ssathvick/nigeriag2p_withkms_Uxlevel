import { Register, Tab, Section } from '../types';

export const getRegisterDetails = (id: string, registers: Register[]) => {
    const data = registers.find(r => r.register_id === id);
    return {
        ...data
    };
};

export const getTabDetails = (id: string, tabs: Tab[]) => {
    const data = tabs.find(t => t.tab_id === id);
    return {
        ...data
    };
};

export const getSectionDetails = (id: string, sections: Section[]) => {
    const data = sections.find(s => s.section_id === id);
    return {
        ...data
    };
};
