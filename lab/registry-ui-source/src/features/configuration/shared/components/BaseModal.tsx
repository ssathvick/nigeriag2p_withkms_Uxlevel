'use client';
import {useEffect,useId,useRef,type ReactNode} from 'react';
import {createPortal} from 'react-dom';
import {X} from 'lucide-react';
import './configuration-workspace.css';
import {useTranslations} from 'next-intl';
interface BaseModalProps{title:string;onClose:()=>void;children:ReactNode;primaryActionLabel?:string;onPrimaryAction?:()=>void;maxWidth?:string;hideCancel?:boolean;secondaryActionLabel?:string}
export default function BaseModal({title,onClose,children,primaryActionLabel,onPrimaryAction,maxWidth='max-w-150',hideCancel=false,secondaryActionLabel}:BaseModalProps){
 const t=useTranslations(),id=useId(),panel=useRef<HTMLDivElement>(null),close=useRef(onClose);close.current=onClose;
 useEffect(()=>{const trigger=document.activeElement as HTMLElement|null,overflow=document.body.style.overflow;document.body.style.overflow='hidden';panel.current?.querySelector<HTMLElement>('input,select,textarea,button')?.focus();return()=>{document.body.style.overflow=overflow;trigger?.focus()}},[]);
 function handleKeyDown(e:React.KeyboardEvent){
  if(e.key==='Escape'){e.stopPropagation();close.current();return}
  if(e.key!=='Tab')return;
  const nodes=panel.current?.querySelectorAll<HTMLElement>('button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),a[href],[tabindex="0"]');
  const all=nodes?[...nodes].filter(n=>n.getBoundingClientRect().width>0):[];
  if(!all.length)return;const first=all[0],last=all[all.length-1];
  if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
 }
 return createPortal(<div className="configuration-modal-overlay" onKeyDown={handleKeyDown}><div ref={panel} role="dialog" aria-modal="true" aria-labelledby={id} className={`configuration-dialog ${maxWidth}`}><header><h2 id={id}>{title}</h2><button type="button" onClick={onClose} aria-label="Close dialog"><X size={23}/></button></header><div className="configuration-dialog-content modal-scroll">{children}{(!hideCancel||primaryActionLabel&&onPrimaryAction)&&<div className="configuration-dialog-actions">{!hideCancel&&<button type="button" onClick={onClose} className="configuration-secondary-button">{secondaryActionLabel||t('cancel')}</button>}{primaryActionLabel&&onPrimaryAction&&<button type="button" onClick={onPrimaryAction} className="configuration-primary-button">{primaryActionLabel}</button>}</div>}</div></div></div>,document.body);
}
