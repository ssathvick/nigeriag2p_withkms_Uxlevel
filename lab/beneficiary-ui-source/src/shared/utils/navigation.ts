import { MenuItem } from "@/shared/types/menuitem";

export const getMenuItems = (locale: string): MenuItem[] => [
    { name: "Dashboard", href: `/${locale}/dashboard`, icon: "/leftmenu_dashboard_01.png" },
    { name: "My Programs", href: `/${locale}/programs`, icon: "/leftmenu_programs_02.png" },
    { name: "Total Benefits", href: `/${locale}/benefits`, icon: "/leftmenu_benefits_03.png" },
    { name: "Bank Accounts", href: `/${locale}/accounts`, icon: "/leftmenu_bankaccount_04.png" },
    { name: "My Registries", href: `/${locale}/registries`, icon: "/leftmenu_registries_05.png" },
    { name: "Applications", href: `/${locale}/applications`, icon: "/leftmenu_schemes_06.png" },
    { name: "Notifications", href: `/${locale}/notifications`, icon: "/leftmenu_notifications_07.png" },
    { name: "Complaints", href: `/${locale}/complaints`, icon: "/leftmenu_complaints_08.png" },
    { name: "News", href: `/${locale}/news`, icon: "/leftmenu_news_09.png" },
];

export const getRouteToIndex = (locale: string): Record<string, number> =>
    getMenuItems(locale).reduce((acc, item, index) => {
        acc[item.href] = index;
        return acc;
    }, {} as Record<string, number>);
