"""Source-bound state economic evidence. Never allocate GDP to smaller areas."""
import re

URL = 'https://documents1.worldbank.org/curated/en/099100825010038474/pdf/P513192-b0cb6210-6cdc-423f-b0eb-834a44a28494.pdf'
SECTORS = {'Crop':('crop_share','Crop production (agriculture)'), 'Livestock production':('livestock_share','Livestock (agriculture)'), 'Trade':('trade_share','Trade'), 'Construction':('construction_share','Construction'), 'Cement':('cement_share','Cement manufacturing'), 'Crude':('oil_share','Crude oil'), 'Crude oil and natural gas':('oil_share','Crude oil and natural gas')}

def add_economy(data, raw):
    def norm(s): return re.sub('[^a-z]', '', s.lower()).replace('federalcapitalterritory','fct').replace('abuja','')
    states={norm(s['name']):s for s in data['states']}
    text=(raw/'worldbank-ndu-2025.txt').read_text()
    common={'year':2023,'url':URL,'classification':'published','license':'World Bank published statistical facts, attributed to NBS and World Bank; original report retained by publisher.'}
    data['sources']['state_economy']={**common,'name':'World Bank / NBS state economy, Box 1','note':'October 2025 Nigeria Development Update, printed page 5. Rounded 2023 figures explicitly printed in the text only: GDP totals for 3 states, national GDP shares for 6, and GDP per capita for 6. Incomplete coverage; not a national ranking. GDP per capita is output per person, not household income or salary. Published per-capita figures are retained; the atlas does not divide 2023 GDP by its 2020 population layer.'}
    data['sources']['state_sectors']={**common,'name':'World Bank / NBS sector shares, Annex 3','note':'October 2025 Nigeria Development Update, printed page 53. The three reported leading sectors for all 36 states and FCT, as shares of each state’s 2023 GDP. Not a complete sector breakdown. An unlisted sector is unknown, not zero. Crop and livestock are separate agricultural activities, not total agriculture. Source labels and values retained; charts sort by numeric share (the source lists Sokoto’s second and third sectors out of size order). No LGA or constituency allocation.'}
    def metric(value,source,unit,**extra):return {'value':value,'source':source,'year':2023,'level':'state','classification':'published','unit':unit,**extra}
    # Values are transcribed only where Box 1 explicitly prints a number.
    totals={'lagos':33.1,'delta':14.6,'fct':9.4}
    shares={'lagos':11.7,'delta':5.2,'fct':3.3,'jigawa':1.5,'yobe':1.0,'gombe':1.1}
    per_capita={'fct':3.1,'lagos':2.1,'kwara':2.0,'borno':.5,'zamfara':.6,'jigawa':.6}
    for key,values,scale,unit in [('gdp',totals,1e12,'NGN, current prices'),('gdp_share',shares,1,'% of national GDP'),('gdp_per_capita',per_capita,1e6,'NGN per person')]:
        for state,value in values.items():states[state]['metrics'][key]=metric(round(value*scale,1),'state_economy',unit,qualification='Rounded published figure; partial state coverage. Not household income.')
    block=text[text.rindex('Annex 3: Sectoral decomposition of state GDP (2023)'):]
    seen=set()
    for line in block.splitlines():
        parts=re.split(r'\s{2,}',line.strip())
        if len(parts)!=4 or norm(parts[0]) not in states:continue
        state=states[norm(parts[0])];seen.add(state['id']);state['economic_sectors']=[]
        for cell in parts[1:]:
            match=re.fullmatch(r'(.+?) \((\d+\.\d+)%\)',cell);assert match,cell
            label,value=match.groups();key,title=SECTORS[label];m=metric(float(value),'state_sectors','%',qualification='Reported top-three sector only; unlisted sectors are not zero.',sector_label=title)
            state['metrics'][key]=m;state['economic_sectors'].append({'key':key,'name':title,'source_label':label})
        assert len(state['economic_sectors'])==3
        assert sum(state['metrics'][s['key']]['value'] for s in state['economic_sectors'])<=100.1
    assert len(seen)==37,len(seen)
    data['coverage']['economy']={'year':2023,'gdp_states':3,'national_share_states':6,'gdp_per_capita_states':6,'top_three_sector_states':37,'household_income_states':0,'lga_or_constituency_estimates':0}
    data['gaps'].append('Economic evidence is state-level and partial: 3 GDP totals, 6 national shares, 6 GDP-per-capita figures and top-three sector shares for 37 areas (2023). Household per-capita income and complete sector accounts are unavailable. No economic values are allocated to LGAs or constituencies.')
