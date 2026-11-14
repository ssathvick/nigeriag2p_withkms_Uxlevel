'use client';
import {useRef,useState} from 'react';
import {Bell,X} from 'lucide-react';
import {useClickOutside} from '@/shared/hooks/useClickOutside';
import {useNotification} from '@/context/GlobalContext';
import {registryDisplayText} from '@/shared/utils/registryDisplayText';
export default function NotificationDropdown(){
 const [open,setOpen]=useState(false),root=useRef<HTMLDivElement>(null),trigger=useRef<HTMLButtonElement>(null);const {notifications,unreadCount,isLoading,isAvailable}=useNotification();useClickOutside(root,()=>setOpen(false),open);
 const close=()=>{setOpen(false);trigger.current?.focus()};
 if(!isAvailable)return null;
 return <div className="relative" ref={root} onKeyDown={e=>{if(e.key==='Escape')close()}}><button ref={trigger} type="button" className="application-notification-trigger" aria-label="Notifications" aria-expanded={open} aria-haspopup="dialog" onClick={()=>setOpen(!open)}><Bell size={23}/>{unreadCount>0&&<span className="application-unread-dot">{unreadCount>99?'99+':unreadCount}</span>}</button>{open&&<section role="dialog" aria-label="Notifications" className="application-header-popover"><header><h2>Notifications</h2><button type="button" aria-label="Close notifications" onClick={close}><X size={17}/></button></header>{isLoading?<p role="status" className="application-empty">Loading notifications…</p>:notifications.length?<ul className="application-notifications">{notifications.map(n=><li key={n.id}><h3>{registryDisplayText(n.subject||'Notification')}</h3><p>{registryDisplayText(n.body||'')}</p></li>)}</ul>:<p className="application-empty">No notifications yet.</p>}</section>}</div>;
}
