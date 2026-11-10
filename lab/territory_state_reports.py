"""Independent publisher reports, never merged into the 2023 comparison series."""
import re,json

REPORT_URLS={
 'nbs-state-gdp-2017.pdf':'https://nigerianstat.gov.ng/pdfuploads/State_Nominal_GDP_2013_-_2017.cdr_%28MAY_2019%29.pdf',
 'jigawa-gdp-2023.pdf':'https://sbs.jigawastate.gov.ng/storage/publications/01KYSMNWSSJ38P917SXJGM4GW1.pdf',
 'delta-gdp-2022.pdf':'https://dida.deltastate.gov.ng/wp-content/uploads/2025/07/2022-GDP2.pdf'}

def add_state_reports(data,raw):
    def norm(s):return re.sub('[^a-z]','',s.lower()).replace('federalcapitalterritory','fct').replace('abuja','')
    states={norm(a['name']):a for a in data['states']};reports=[]
    def source(key,name,year,file,note):
        data['sources'][key]={'name':name,'year':year,'url':REPORT_URLS[file],'classification':'published','note':note,'license':'Published statistical facts extracted with attribution; original document remains with publisher.'}
    source('nbs_2017','NBS State Nominal GDP, May 2019 appendix',2017,'nbs-state-gdp-2017.pdf','Historical 2017 current-basic-price accounts for 22 states/FCT only. PDF page 186 (2017 appendix). Original table amounts are NGN million, converted to NGN. This is not the rebased 2023 series. Appendix Akwa Ibom GDP (5,142,862.45 million) differs from page 3 summary (5,141,068.15 million); appendix value retained and reconciliation disclosed. Printed dashes stay unavailable, not zero. Parent sectors and child activities are never added together. No matched population denominator or per-capita estimate supplied.')
    source('jigawa_2023','Jigawa State Bureau of Statistics: GDP 2019–2023',2023,'jigawa-gdp-2023.pdf','PDF page 2 supplies GDP at current basic prices in NGN million. Detailed sector series on PDF pages 7–18 are used; page 6 supplies broad aggregates. The page 3 infographic says agriculture 33.60%, conflicting with 36.60% on pages 6 and 7; the repeated detailed-series figure is retained with this qualification. State report differs from the World Bank Annex 3 series and is kept separate. No matched 2023 population denominator or GDP-per-person figure verified.')
    source('delta_2022','Delta State GDP 2021 & 2022 report',2022,'delta-gdp-2022.pdf','Tables 3.1a (printed pages 8–9) and 3.3 (page 25). Sector values and GDP at current basic prices; a separate GDP at market prices includes net indirect product taxes. GDP per person uses the report’s 2022 market-price GDP and projected population. The report calls it per-capita income, but it is GDP divided by population, not measured household income. Different vintage and year from the World Bank 2023 series; never combined for rankings. Blank activity rows remain unavailable.')
    def m(value,src,unit,**extra):return {'value':value,'source':src,'year':data['sources'][src]['year'],'level':'state','classification':'published','unit':unit,**extra}
    def sector(name,value,src,group=True):return {'name':name.title(),'group':group,'metric':m(value,src,'NGN') if value is not None else None,'missing_reason':'Source dash / blank; not converted to zero' if value is None else ''}
    # Column order is checked against the source header; 22 state columns + total.
    names=['Akwa Ibom','Bayelsa','Cross River','Delta','Kaduna','Kano','Ogun','Osun','Oyo','Rivers','Zamfara','Anambra','Bauchi','Ebonyi','Edo','Ekiti','Gombe','Jigawa','Kogi','Niger','Ondo','FCT']
    page=(raw/'nbs-state-gdp-2017.txt').read_text().split('\f')[185]
    assert page.startswith(' GROSS DOMESTIC RPODUCT') and '\n2017\n' in page
    rows=[];totals=None
    for line in page.splitlines()[4:]:
        found=re.search(r'\s+(?:\d[\d,]*\.\d{2}|-)(?=\s|$)',line)
        if not found:continue
        label=line[:found.start()].strip()
        if not label:continue
        tokens=line[found.start():].split()
        assert len(tokens)==23,(label,len(tokens))
        values=[None if x=='-' else round(float(x.replace(',',''))*1e6,2) for x in tokens]
        if label=='GDP Current Basic Price':totals=values;continue
        clean=re.sub(r'^\d+\.\s*','',label)
        rows.append((clean,values,clean==clean.upper()))
    assert totals and len(rows)==52,len(rows)
    for idx,name in enumerate(names):
        s=states[norm(name)];sectors=[sector(label,values[idx],'nbs_2017',group) for label,values,group in rows]
        parent_sum=sum(x['metric']['value'] for x in sectors if x['group'] and x['metric'])
        report={'id':'nbs-2017-'+s['id'],'state_id':s['id'],'state_name':s['name'],'year':2017,'source':'nbs_2017','basis':'Current basic prices · historical NBS series','gdp':m(totals[idx],'nbs_2017','NGN'),'sectors':sectors,'sector_unit':'NGN','notes':['Historical source-specific report; not comparable with the rebased 2023 series.','No verified same-year population denominator; GDP per person remains unavailable.'],'reconciliation_difference_ngn':round(parent_sum-totals[idx],2)}
        if abs(parent_sum-totals[idx])>1e6:report['notes'].append('Source sector totals do not reconcile to the printed GDP. Values are preserved, not rescaled; see reconciliation difference.')
        if name=='Akwa Ibom':report['notes'].append('The report’s summary and appendix disagree on GDP; this view uses the appendix value and flags the discrepancy.')
        reports.append(report)
    # Jigawa: parse the ordered detailed-series labels and their five percentages.
    pages=(raw/'jigawa-gdp-2023.txt').read_text().split('\f');jrows=[]
    for p in pages[6:18]:
        label=[]
        for line in p.splitlines():
            line=line.strip()
            if not line or line.startswith('JIGAWA STATE') or line.startswith('Start (Base') or line.startswith('Growth compared') or line.startswith('Decline compared') or line.startswith('No change') or line.startswith('GDP sector not'):continue
            if re.fullmatch(r'(?:20\d{2}\s*){5}',line):continue
            values=re.findall(r'\d+\.\d+%?',line)
            dashed=re.fullmatch(r'(?:[-.]\s*){5}',line)
            if len(values)==5 or dashed:
                title=' '.join(label).strip();label=[]
                assert title,title
                val=float(values[-1].rstrip('%')) if values else None
                jrows.append({'name':title.title(),'group':title==title.upper(),'metric':m(val,'jigawa_2023','%') if val is not None else None,'missing_reason':'Source dash; not converted to zero' if val is None else ''})
            elif re.search('[A-Za-z]',line):label.append(line)
    assert len(jrows)==52,len(jrows)
    assert next(x['metric']['value'] for x in jrows if x['name']=='Agriculture')==36.6
    jigawa_total=re.findall(r'N([\d,]+\.\d+)',pages[1]);assert len(jigawa_total)==5
    reports.append({'id':'jigawa-2023','state_id':states['jigawa']['id'],'state_name':'Jigawa','year':2023,'source':'jigawa_2023','basis':'Current basic prices · Jigawa publication','gdp':m(float(jigawa_total[-1].replace(',',''))*1e6,'jigawa_2023','NGN'),'sectors':jrows,'sector_unit':'%','notes':['This source differs from World Bank Annex 3. It is not substituted into the comparable-series map.','Agriculture: 36.60% on detailed pages 6–7; page 3 infographic says 33.60%. Detailed series retained.','No verified same-year population denominator; GDP per person remains unavailable.']})
    # Delta: retain the 2022 column only. Wrapped descriptions are joined before parsing.
    text=(raw/'delta-gdp-2022.txt').read_text();block=text[text.index('Table 3.1a:'):text.index('Table 3.1b:')]
    block=block.replace('22. ELECTRICITY, GAS ,STEAM AND AIR CONDITIONING   108,245.70\n                                                      SUPPLY','22. ELECTRICITY, GAS ,STEAM AND AIR CONDITIONING SUPPLY   108,245.70')
    block=block.replace('23. WATER SUPPLY,SEWERAGE, WASTE MANAGEMENT AND       2,357.64\n                                                           REMEDIATION','23. WATER SUPPLY,SEWERAGE, WASTE MANAGEMENT AND REMEDIATION   2,357.64')
    block=block.replace('41. PROFESSIONAL, SCIENTIFIC AND TECHNICAL SERVICES\n','41. PROFESSIONAL, SCIENTIFIC AND TECHNICAL SERVICES ')
    block=block.replace('REMEDIATION   2,357.64\n','REMEDIATION   2,357.64 ')
    block=block.replace('34. Motion Pictures, Sound recording and Music 14,941.32\n                                                     production','35. Motion Pictures, Sound recording and Music production 14,941.32')
    drows=[];dmetrics={}
    for line in block.splitlines():
        found=re.search(r'\s+\d[\d,]*\.\d{2}',line)
        if found:
            label=line[:found.start()].strip();numbers=re.findall(r'\d[\d,]*\.\d{2}',line[found.start():])
            if len(numbers)!=10:continue
            value=round(float(numbers[-1].replace(',',''))*1e6,2)
            if label.startswith('GDP Current') or label.startswith('Net Indirect'):dmetrics[label]=value;continue
            clean=re.sub(r'^\d+\.\s*','',label);drows.append(sector(clean,value,'delta_2022',clean==clean.upper()))
        elif re.match(r'^\s+\d+\.\s+[A-Za-z]',line):
            clean=re.sub(r'^\d+\.\s*','',line.strip());drows.append(sector(clean,None,'delta_2022',False))
    assert len(drows)==52,[x['name'] for x in drows]
    t3=text[text.index('Table 3.3:'):text.index('Figure 3.21:')]
    def last(label):
        row=next(x for x in t3.splitlines() if x.startswith(label));return float(re.findall(r'\d[\d,]*(?:\.\d+)?',row[len(label):])[-1].replace(',',''))
    pop=last('Delta State Population projeected');pc=last('Per Capita Inome in Nigerian Naira (NGN)')
    assert abs(dmetrics['GDP Current Market Price']/pop-pc)<.02
    reports.append({'id':'delta-2022','state_id':states['delta']['id'],'state_name':'Delta','year':2022,'source':'delta_2022','basis':'Sector accounts: current basic prices; per-person output: market prices','gdp':m(dmetrics['GDP Current Basic Price'],'delta_2022','NGN'),'gdp_market':m(dmetrics['GDP Current Market Price'],'delta_2022','NGN'),'gdp_per_capita':m(pc,'delta_2022','NGN per person',qualification='Published market-price GDP divided by projected population; not household income.'),'population':{**m(pop,'delta_2022','people'),'classification':'modelled','qualification':'Publisher’s 2022 population projection, not a census count.'},'sectors':drows,'sector_unit':'NGN','notes':['Independent 2022 report; kept outside the rebased 2023 comparison.','Per-person GDP = market-price GDP / the report’s same-year projected population. Sector shares use basic-price GDP.'],'reconciliation_difference_ngn':round(sum(x['metric']['value'] for x in drows if x['group'] and x['metric'])-dmetrics['GDP Current Basic Price'],2)})
    # NGF profiles preserve their own provenance; no inferred price basis or per-capita ratio.
    ngf=json.loads((raw/'ngf-gdp-2023.json').read_text())
    assert len(ngf)==36 and all(x.get('gdp_ngn',0)>0 for x in ngf)
    for x in ngf:
        key='ngf_2023_'+x['state_id']
        note='NGF public state profile, retrieved 4 November 2026. GDP reference year 2023; original unit NGN million. Price basis, base year and underlying estimation methodology are not specified on the profile. Its population is dated 2025 and is not used as a 2023 denominator. No numeric sector breakdown or GDP per person is supplied. Published-source figure, not independently validated national accounts.'
        data['sources'][key]={'name':'Nigeria Governors’ Forum · '+x['state_name']+' profile','year':2023,'url':x['url'],'classification':'published','note':note,'license':'Published statistical fact with attribution; original page remains with publisher.'}
        reports.append({'id':'ngf-2023-'+x['state_id'],'state_id':x['state_id'],'state_name':x['state_name'],'year':2023,'source':key,'publisher_label':'NGF profile','basis':'NGF published GDP · price basis and methodology unspecified','labels':{'gdp':'GDP · price basis unspecified'},'gdp':m(x['gdp_ngn'],key,'NGN',qualification=note),'sectors':[],'sector_unit':'NGN','notes':['Verified against the NGF publisher page; the underlying accounts and price basis are not documented there. Kept separate from World Bank and state statistical reports.','The profile lists 2025 population alongside 2023 GDP. No cross-year per-person estimate has been calculated.','No quantitative sector breakdown is supplied by this profile.']})
    key='lagos_ledu_2024'
    note='Lagos Economic Development Update 2025: printed page 29 (PDF page 30) projects 2024 real GDP per person at US$5,043; Figure 2.12 labels the measure PPP. Printed page 59 (PDF page 60) projects 2024 nominal GDP at NGN54.77 trillion. Both are forecasts, not observed outcomes. Nominal GDP and real PPP GDP per person use different price bases; do not divide one by the other to infer population. Real/PPP base year is not stated in these passages.'
    data['sources'][key]={'name':'Lagos MEPB · Economic Development Update 2025','year':2024,'url':'https://lagosmepb.org/wp-content/uploads/2025_lagos_economic_development_update.pdf','classification':'modelled','note':note,'license':'Published statistical facts with attribution.'}
    reports.append({'id':'lagos-ledu-2024-forecast','state_id':states['lagos']['id'],'state_name':'Lagos','year':2024,'source':key,'publisher_label':'Lagos LEDU · forecast','basis':'2024 forecast · nominal NGN GDP; real PPP US$ per person','labels':{'gdp':'Nominal GDP · forecast','gdp_per_capita':'Real GDP per person · PPP forecast'},'gdp':{**m(54770000000000,key,'NGN'),'classification':'modelled','qualification':note},'gdp_per_capita':{**m(5043,key,'PPP US$ per person'),'classification':'modelled','qualification':note},'sectors':[],'sector_unit':'NGN','notes':['Publisher forecast for 2024, issued in its 2025 report; not a confirmed actual GDP or income observation.','GDP is nominal naira; GDP per person is real purchasing-power-parity US dollars. These measures must not be used together to infer population.','The real/PPP base year and a full quantitative sector breakdown are not verified here. Kept outside all comparable-series rankings.']})
    data['economic_reports']=reports
    data['coverage']['economy']['independent_reports']=len(reports)
    data['coverage']['economy']['independent_report_states']=len(set(x['state_id'] for x in reports))
    data['gaps'].append('Separate economic-report library: NBS 2017 accounts for 22 states/FCT, Jigawa 2023 and Delta 2022. These vintages are not merged into the World Bank 2023 comparisons. NGF 2023 profiles add published GDP for all 36 states, with unspecified price basis; FCT retains its separate historical report. Complete matched-year GDP and per-capita coverage remains unavailable.')


