'use client';
import {useState} from 'react';
import {useTranslations} from 'next-intl';
import BaseModal from '@/features/configuration/shared/components/BaseModal';
interface Props{onClose:()=>void;rawJson:object|null;transformedJson:object|null;enrichedJson:object|null;loading?:boolean}
export default function MessagePopup({onClose,rawJson,transformedJson,enrichedJson,loading}:Props){const t=useTranslations(),[active,setActive]=useState(0);const tabs=[{label:t('raw_message'),data:rawJson},{label:t('enriched_message'),data:enrichedJson},{label:t('transformed_message'),data:transformedJson}];return <BaseModal title="Message details" onClose={onClose} maxWidth="max-w-4xl" secondaryActionLabel={t('close')}><div role="tablist" aria-label="Message payload" className="application-payload-tabs">{tabs.map((tab,i)=><button key={tab.label} type="button" role="tab" aria-selected={active===i} onClick={()=>setActive(i)}>{tab.label}</button>)}</div><div role="tabpanel" className="application-payload-data">{loading?<p role="status">Loading message…</p>:<pre>{JSON.stringify(tabs[active].data,null,2)||'No message data available.'}</pre>}</div></BaseModal>}
