'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Image from 'next/image';
import { OpenID4VPVerification } from 'inji-sdk';
import { buildPayloadFromDecodedJWT, decodeSdJwtToken } from '@/features/verifiable-credentials/utils';
import { PayloadView, StatusView } from '@/features/verifiable-credentials/components';
import { useRuntimeConfig } from '@/context/RuntimeConfigContext';
import { useTranslations } from 'next-intl';
import { useFetch } from '@/shared/hooks';

interface Props {
    vc: any;
    onClose: () => void;
}

export default function VpVerificationModal({
    vc,
    onClose,
}: Props) {
    const t = useTranslations();
    const { config } = useRuntimeConfig();

    const [verificationComplete, setVerificationComplete] = useState(false);
    const [verificationStatus, setVerificationStatus] = useState<'idle' | 'verifying' | 'success' | 'error'>('idle');
    const { execute: importVC } = useFetch();

    const [verificationResult, setVerificationResult] = useState<any>(null);

    const [error, setError] = useState<string | null>(null);

    // Todo: get the id and purpose from backend once the implementation is done!
    const presentationDefinition = useMemo(() => {
        return {
            id: "7f3c2a91-bb84-4d1f-9a6e-41c8e5a0d9f2",
            purpose: "Digital identity verification for registry onboarding",
            format: {
                ldp_vc: {
                    proof_type: ["Ed25519Signature2020", "EdDSA", "ES256"],
                },
            },
            input_descriptors: [vc.descriptor_schema],
        };
    }, [vc.descriptor_schema]);

    const [activeTab, setActiveTab] = useState<'status' | 'payload'>('status');

    const [importResult, setImportResult] = useState<any>(null);
    const [isImporting, setIsImporting] = useState(false);


    const handleVPProcessed = async (result: any[]) => {
        const processedResult = await Promise.all(
            result.map(async (vpResult) => {
                if (typeof vpResult?.vc !== "string") return vpResult;

                try {
                    const { decodedJwt, regularClaims, disclosedClaims, decoded } = await decodeSdJwtToken(vpResult.vc);

                    const payload = buildPayloadFromDecodedJWT(decodedJwt, regularClaims, disclosedClaims);

                    return {
                        ...vpResult,
                        vc: decoded,
                    };
                } catch (e) {
                    console.error("SD-JWT decode failed:", e);
                    return vpResult;
                }
            })
        );

        setVerificationResult(processedResult);
        setVerificationStatus("success");
        setVerificationComplete(true)
    };



    const handleError = (error: any) => {
        setError(error.message);
        setVerificationStatus('error');
    };

    const handleQrCodeExpired = () => {
        setError('QR code has expired. Please try again.');
        setVerificationStatus('error');
    };

    const handleStartVerification = useCallback(() => {
        setVerificationStatus('verifying');
        setVerificationResult(null);
        setError(null);

        setTimeout(() => {
            const triggerButton = document.getElementById('vp-verification-trigger');
            triggerButton?.click();
        }, 100);
    }, []);


    useEffect(() => {
        handleStartVerification();
    }, [handleStartVerification]);


    const handleReset = useCallback(() => {
        setVerificationStatus('idle');
        setVerificationResult(null);
        setError(null);
        handleStartVerification()
    }, []);

    const handleImport = useCallback(async (data: any[]) => {
        try {
            const vcPayload = data?.[0]?.vc;
            if (!vcPayload) return;

            setIsImporting(true);
            setError(null);

            const result = await importVC(
                '/api/input-mechanism/ingest-data',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        vc_payload: vcPayload,
                        register_id: vc.register_id,
                        intake_form_id: vc.intake_form_id,
                        data_model_mnemonic: vc.data_model_mnemonic,
                    }),
                }
            );

            setImportResult(result);
            setVerificationComplete(true);
        } catch (err) {
            console.error('Import error:', err);
            setError('Failed to import verified credential');
        } finally {
            setIsImporting(false);
        }
    }, [
        importVC,
        vc.register_id,
        vc.intake_form_id,
        vc.data_model_id,
    ]);


    return (
        <div className="fixed inset-0 bg-neutral-first/80 flex justify-center items-center z-50">
            <div
                className={`relative bg-neutral-second rounded-[10px] p-10 border-10 border-primary-first flex flex-col transition-all duration-300 ${verificationStatus === 'success' ? 'w-200 h-160' : 'w-150 h-120'}`}
            >
                <div
                    className={`flex items-center mb-3 transition-all ${verificationComplete ? 'justify-between' : 'justify-center relative'}`}
                >
                    <h2
                        className={`text-xl font-semibold transition-all ${verificationComplete ? 'text-left' : 'text-center'}`}
                    >
                        {t('verify_credential') || 'Verify Credential'}
                    </h2>

                    <button
                        onClick={onClose}
                        className={`opacity-60 hover:opacity-100 transition-all ${verificationComplete ? 'static' : 'absolute right-0'}`}
                    >
                        <Image src="/images/changerequest/cr_close.png" alt="Close" width={30} height={30} />
                    </button>
                </div>

                <div className="flex flex-col h-full">
                    {importResult ? (
                        <div className="flex flex-col items-center justify-center h-full text-center px-6">
                            <Image src="/images/common/verified.png" alt="success" width={60} height={60} />

                            <h3 className="text-[22px] font-semibold mt-4">
                                {t('import_successful') || 'Import Successful'}
                            </h3>

                            <p className="text-neutral-first/70 mt-2">
                                {t('import_success_msg') || 'Credential was successfully ingested'}
                            </p>

                            <div className="mt-6 w-full bg-secondary-first rounded-[20px] p-4 text-center text-sm">
                                {/* <p>
                                    <span className="font-medium">{t('status') || 'Status'}:</span>{' '}
                                    <span className="text-toast-success">
                                        {importResult.message.ack_status}
                                    </span>
                                </p> */}
                                <p>
                                    <span className="font-medium">{t('correlation_id') || 'Correlation ID'}:</span>{' '}
                                    {importResult.correlation_id}
                                </p>
                            </div>

                            <button
                                onClick={onClose}
                                className="mt-6 bg-neutral-first text-neutral-second px-10 py-2 rounded-[20px]"
                            >
                                {t('close') || 'Close'}
                            </button>
                        </div>
                    ) : verificationStatus === 'success' && verificationResult ? (
                        <>
                            <div className="flex gap-2 mb-3">
                                <button
                                    onClick={() => setActiveTab('status')}
                                    className={`px-8 py-2 rounded-t-[20px] text-[18px] font-medium ${activeTab === 'status'
                                        ? 'bg-primary-first text-neutral-first'
                                        : 'bg-secondary-second text-neutral-first'
                                        }`}
                                >
                                    {t('status') || 'Status'}
                                </button>

                                <button
                                    onClick={() => setActiveTab('payload')}
                                    className={`px-8 py-2 rounded-t-[20px] text-[18px] font-medium ${activeTab === 'payload'
                                        ? 'bg-primary-first text-neutral-first'
                                        : 'bg-secondary-second text-neutral-first'
                                        }`}
                                >
                                    {t('payload') || 'Payload'}
                                </button>
                            </div>

                            {activeTab === 'status' ? (
                                <StatusView vp={verificationResult[0]} />
                            ) : (
                                <PayloadView data={verificationResult} />
                            )}

                            <div className="my-6 flex justify-center">
                                <button
                                    onClick={() => handleImport(verificationResult)}
                                    disabled={isImporting}
                                    className="bg-neutral-first text-neutral-second px-10 py-2 rounded-[20px] disabled:opacity-50"
                                >
                                    {isImporting ? t('importing') || 'Importing…' : t('import') || 'Import'}
                                </button>

                            </div>
                        </>
                    ) : verificationStatus === 'error' ? (
                        <div className="flex flex-col items-center justify-center h-full text-center px-6">
                            <p className="text-[18px] text-neutral-first mb-6">
                                {error || t('verify_error_msg') || 'We could not verify the credential. Please try scanning again.'}
                            </p>

                            <div className="flex gap-4">
                                <button
                                    onClick={handleReset}
                                    className="bg-neutral-first text-neutral-second px-8 py-2 rounded-[20px]"
                                >
                                    {t('try_again') || 'Try again'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-center">
                            <OpenID4VPVerification
                                verifyServiceUrl={config?.verifyServiceUrl}
                                presentationDefinition={presentationDefinition}
                                onVPProcessed={handleVPProcessed}
                                onError={handleError}
                                onQrCodeExpired={handleQrCodeExpired}
                                isSameDeviceFlowEnabled={false}
                                clientId={config?.vpClientId!}
                                triggerElement={
                                    <button
                                        id="vp-verification-trigger"
                                        style={{ display: 'none' }}
                                        aria-label="Start VP Verification"
                                    />
                                }
                                qrCodeStyles={{
                                    size: 200,
                                    borderRadius: 16,
                                    bgColor: 'var(--color-neutral-second)',
                                    fgColor: 'var(--color-neutral-first)',
                                }}
                            />
                            <div className="flex flex-col items-center gap-3">
                                <p className="font-medium">{t('importing_data') || 'Importing your data'}</p>
                                <p className="text-sm text-neutral-first/50">{t('please_wait') || 'Please wait a few moments'}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
