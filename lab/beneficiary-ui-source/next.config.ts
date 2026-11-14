import { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin();

const nextConfig: NextConfig = {
    basePath: "/portal",
    output: "standalone",
    poweredByHeader: false,
    allowedDevOrigins: ["portal.openg2p.my", "*.portal.openg2p.my"],

    // Ignore ESLint errors during production build
    eslint: {
        ignoreDuringBuilds: true,
    },
};

export default withNextIntl(nextConfig);
