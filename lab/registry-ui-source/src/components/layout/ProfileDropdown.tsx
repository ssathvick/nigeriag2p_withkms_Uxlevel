'use client';
import {useRef,useState} from 'react';
import Image from 'next/image';
import {useClickOutside} from '@/shared/hooks/useClickOutside';
import {useAuth} from '@/context/Authcontext';
import {useTranslations} from 'next-intl';
export default function ProfileDropdown(){
 const [open,setOpen]=useState(false),root=useRef<HTMLDivElement>(null),trigger=useRef<HTMLButtonElement>(null),{user,logout}=useAuth(),t=useTranslations();const displayName=user?.name||t('user');useClickOutside(root,()=>setOpen(false),open);
 return <div ref={root} className="relative" onKeyDown={e=>{if(e.key==='Escape'){setOpen(false);trigger.current?.focus()}}}><button ref={trigger} type="button" aria-label={displayName+' profile menu'} aria-expanded={open} aria-haspopup="true" onClick={()=>setOpen(!open)} className="flex items-center gap-3 px-1 py-1 text-neutral-first"><span className="hidden sm:inline text-[16px]">{displayName}</span><Image src="/images/common/user_image.png" alt="" width={38} height={38} className="rounded-full"/></button>{open&&<div className="application-header-popover application-profile-menu"><p>{displayName}</p><button type="button" onClick={logout}><Image src="/images/common/logout.png" alt="" width={17} height={17}/>{t('logout')}</button></div>}</div>;
}
