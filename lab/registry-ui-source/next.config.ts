import type { NextConfig } from "next";

import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

const isDev = process.env.NODE_ENV === 'development';

const cspHeader = `
    default-src 'self';
    script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ''};
    style-src 'self' 'unsafe-inline';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';

    frame-src 'self' https://esignet.nsr.openg2p.org;

    frame-ancestors 'none';
    // ${isDev ? '' : 'upgrade-insecure-requests;'}
`;

const nextConfig: NextConfig = {
    output: "standalone",
    reactCompiler: true,
    async headers() {
        return [
            {
                source: '/(.*)',
                headers: [
                    {
                        key: 'Content-Security-Policy',
                        value: cspHeader.replace(/\n/g, '').trim(),
                    },
                ],
            },
        ];
    },
    webpack: (config: any, { dev }: any) => {
        // Keep existing dev watch options for better hot reloading
        if (dev) {
            config.watchOptions = {
                poll: 1000,
                aggregateTimeout: 300,
            };
        }

        // Silence noisy third‑party warnings to keep build output clean
        config.ignoreWarnings = [
            ...(config.ignoreWarnings || []),
            // Silence dynamic require warning from `inji-sdk`
            {
                module: /inji-sdk[\\/]dist[\\/]index\.js/,
                message: /Critical dependency: the request of a dependency is an expression/,
            },
        ];

        return config;
    },
};

export default withNextIntl(nextConfig);
