import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/shared/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/commons/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    first: "var(--color-primary-first)",
                    second: "var(--color-primary-second)",
                },
                secondary: {
                    first: "var(--color-secondary-first)",
                    second: "var(--color-secondary-second)",
                    third: "var(--color-secondary-third)",
                },
                neutral: {
                    first: "var(--color-neutral-first)",
                    second: "var(--color-neutral-second)",
                },
                toast: {
                    info: "var(--toast-info-color)",
                    success: "var(--toast-success-color)",
                    warning: "var(--toast-warning-color)",
                    failed: "var(--toast-failed-color)",
                },
            },
        },
    },
    plugins: [],
};

export default config;
