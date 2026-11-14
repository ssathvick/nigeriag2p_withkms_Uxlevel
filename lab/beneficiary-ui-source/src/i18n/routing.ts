import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
    locales: ("en fr tl").split(/\s+/),
    defaultLocale: "en"
});
