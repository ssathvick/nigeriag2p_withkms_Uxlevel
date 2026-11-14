import type { Metadata } from "next";

import { NotFound as NotFoundComponent } from '@/components/shared';
import { prefixBasePath } from '@/shared/utils/path';

export const metadata: Metadata = {
    title: "Page Not Found - Beneficiary Portal",
    description: "The page you are looking for does not exist in the OpenG2P Beneficiary Portal.",
    icons: {
        icon: prefixBasePath("/logo.png"),
    },
};

export default function NotFound() {
    return <NotFoundComponent />;
}
