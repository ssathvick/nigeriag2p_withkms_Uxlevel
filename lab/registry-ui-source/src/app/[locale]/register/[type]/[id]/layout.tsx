import { RegisterTabsProvider } from '@/context/RegisterTabsContext';
import { RegisterRecordProvider } from '@/context/RegisterRecordContext';

export default function RegisterRecordLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <RegisterTabsProvider>
            <RegisterRecordProvider>
                {children}
            </RegisterRecordProvider>
        </RegisterTabsProvider>
    );
}
