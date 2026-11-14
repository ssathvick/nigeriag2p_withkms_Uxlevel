from pathlib import Path
root=Path(__file__).parent/'registry-ui-source/src/components/ui'
for name in ['StatsCardSmall.tsx','StatsCardLarge.tsx']:
 p=root/name;s=p.read_text();s=s.replace('import { useMemo }',"import {useStatsShortcut} from '@/components/shared/StatsShortcut';\nimport {InfoHint} from '@/components/shared/Workflow';\nimport { useMemo }",1)
 s=s.replace('    const t = useTranslations();','    const t = useTranslations();\n    const navigate=useStatsShortcut(stats_endpoint);',1)
 if name=='StatsCardSmall.tsx':
  s=s.replace('                                {totalCount}','                                <button type="button" aria-label={`View ${title}`} onClick={e=>{e.stopPropagation();navigate()}} className="rounded-full px-2 hover:bg-primary-first/30 focus-visible:outline-2">{totalCount}</button>',1)
  s=s.replace('<li key={row.id} className="flex items-center gap-2">','<li key={row.id} className="flex items-center gap-2">',1)
  s=s.replace('                                <span className="font-roboto text-[16px] font-bold leading-7 truncate overflow-hidden whitespace-nowrap" title={row.value}>\n                                    {row.value}\n                                </span>','''                                <button type="button" onClick={e=>{e.stopPropagation();navigate(row.id)}} aria-label={`View ${row.value || 0} ${row.label}`} className={`rounded-full px-3 py-0.5 font-bold transition-colors hover:bg-primary-first hover:text-neutral-first ${Number(row.value)>0 && (stats_endpoint.includes('tasks') || row.id==='pending' || row.id==='pendingSubmissions' || row.id==='draftSubmissions')?'bg-red-100 text-red-800':'bg-secondary-first text-secondary-third'}`}>{row.value || 0}</button>''')
 else:
  s=s.replace('{(totalCount || 0).toString()}','<button type="button" aria-label={`View ${title}`} onClick={e=>{e.stopPropagation();navigate()}} className="rounded-full px-2 hover:bg-primary-first/30">{(totalCount || 0).toString()}</button>',1)
  s=s.replace('{(row.value || 0).toString()}','<button type="button" aria-label={`View ${row.value || 0} ${row.label}`} onClick={e=>{e.stopPropagation();navigate(row.id)}} className={`rounded-full px-3 py-1 hover:bg-primary-first ${Number(row.value)>0 && row.id===\'pending\'?\'bg-red-100 text-red-800\':\'bg-secondary-first text-secondary-third\'}`}>{(row.value || 0).toString()}</button>',1)
 p.write_text(s)
print('Dashboard counters now open filtered native lists directly.')
