'use client';
import {useEffect,useId,useState} from 'react';
type Option={label:string;value:string};
interface Props{label?:string;options:Option[];value?:string;onChange?:(value:string)=>void;loading?:boolean;placeholder?:string;disabled?:boolean}
export default function CustomDropdown({label,options,value,onChange,loading,placeholder='Select',disabled}:Props){
 const id=useId(),[selected,setSelected]=useState(value??'');useEffect(()=>setSelected(value??''),[value]);
 return <div className="configuration-dropdown">{label&&<label htmlFor={id}>{label}</label>}<select id={id} aria-label={label||placeholder} value={selected} disabled={disabled||loading} onChange={e=>{setSelected(e.target.value);onChange?.(e.target.value)}}><option value="">{loading?'Loading choices…':placeholder}</option>{options.map(opt=><option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></div>;
}
