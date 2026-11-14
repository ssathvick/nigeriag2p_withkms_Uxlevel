'use client';
import {ShieldAlert} from 'lucide-react';
import {useTranslations} from 'next-intl';
import BaseModal from './BaseModal';
import {useConfigurationAccess} from './configurationAccess';
import {useRbac} from '@/context/RbacContext';
interface Props{onConfirm:()=>void;onClose:()=>void;loading?:boolean;messageKey:string}
export default function ConfirmRemovePopup({onConfirm,onClose,loading,messageKey}:Props){const t=useTranslations(),access=useConfigurationAccess(),{can}=useRbac();return <BaseModal title={t('are_you_sure')} onClose={onClose} hideCancel><div className="configuration-remove-message"><ShieldAlert size={36}/><p>{t(messageKey)}</p></div><div className="configuration-dialog-actions"><button type="button" className="configuration-secondary-button" onClick={onClose}>{t('cancel')}</button>{(!access||can(access.delete))&&<button type="button" className="configuration-remove-button" disabled={loading} aria-busy={loading} onClick={onConfirm}>{loading?t('loading'):t('remove')}</button>}</div></BaseModal>}
