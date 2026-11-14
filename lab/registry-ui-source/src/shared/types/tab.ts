export interface TabConfig {
    tab_id: string;
    register_id: string;
    tab_label: string;
    tab_order: number;
}

export interface TabsResponse {
    tabs: TabConfig[];
}
