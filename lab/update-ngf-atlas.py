from pathlib import Path
p=Path('territory_state_reports.py');s=p.read_text();s=s.replace('import re','import re,json',1)
insert='''    # NGF profiles preserve their own provenance; no inferred price basis or per-capita ratio.
    ngf=json.loads((raw/'ngf-gdp-2023.json').read_text())
    assert len(ngf)==36 and all(x.get('gdp_ngn',0)>0 for x in ngf)
    for x in ngf:
        key='ngf_2023_'+x['state_id']
        note='NGF public state profile, retrieved 4 November 2026. GDP reference year 2023; original unit NGN million. Price basis, base year and underlying estimation methodology are not specified on the profile. Its population is dated 2025 and is not used as a 2023 denominator. No numeric sector breakdown or GDP per person is supplied. Published-source figure, not independently validated national accounts.'
        data['sources'][key]={'name':'Nigeria Governors’ Forum · '+x['state_name']+' profile','year':2023,'url':x['url'],'classification':'published','note':note,'license':'Published statistical fact with attribution; original page remains with publisher.'}
        reports.append({'id':'ngf-2023-'+x['state_id'],'state_id':x['state_id'],'state_name':x['state_name'],'year':2023,'source':key,'publisher_label':'NGF profile','basis':'NGF published GDP · price basis and methodology unspecified','labels':{'gdp':'GDP · price basis unspecified'},'gdp':m(x['gdp_ngn'],key,'NGN',qualification=note),'sectors':[],'sector_unit':'NGN','notes':['Verified against the NGF publisher page; the underlying accounts and price basis are not documented there. Kept separate from World Bank and state statistical reports.','The profile lists 2025 population alongside 2023 GDP. No cross-year per-person estimate has been calculated.','No quantitative sector breakdown is supplied by this profile.']})
'''
s=s.replace("    data['economic_reports']=reports",insert+"    data['economic_reports']=reports")
s=s.replace('Complete matched-year GDP and per-capita coverage for 37 areas is still unavailable.','NGF 2023 profiles add published GDP for all 36 states, with unspecified price basis; FCT retains its separate historical report. Complete matched-year GDP and per-capita coverage remains unavailable.')
p.write_text(s)
p=Path('persona-ui/src/economic-reports.jsx');s=p.read_text();s=s.replace("population:'Same-year projected population'}","population:'Same-year projected population',...r.labels}")
s=s.replace('24 reports across 22 state/FCT areas: NBS 2017, Jigawa 2023 and Delta 2022.','{reports.length} reports across {new Set(reports.map(x=>x.state_id)).size} state/FCT areas. Each source and year stays separate.')
s=s.replace("x.source==='nbs_2017'?'NBS historical':'State publication'","x.publisher_label||(x.source==='nbs_2017'?'NBS historical':'State publication')")
s=s.replace('19 sector groups</option>','{r.sectors.filter(s=>s.group).length} sector groups</option>').replace('33 component activities</option>','{r.sectors.filter(s=>!s.group).length} component activities</option>')
s=s.replace('<select value={detail?', '<select disabled={!r.sectors.length} value={detail?')
s=s.replace('Do not add these to the 19 sector groups.','Do not add these to the parent sector groups.')
s=s.replace('<div className="ti-sector-list">','{!r.sectors.length&&<p className="ti-notice">Sector breakdown unavailable in this source. No sector values have been inferred or borrowed from another report.</p>}<div className="ti-sector-list">')
s=s.replace('Coverage remains incomplete for all 37 areas.','GDP reports cover all 37 areas across different sources and years; comparable-year and per-person coverage remains incomplete.')
p.write_text(s)
p=Path('test-territory-data.py');s=p.read_text().replace('self.assertEqual(len(reports),24)','self.assertEqual(len(reports),60)').replace("len({r['state_id'] for r in reports}),22","len({r['state_id'] for r in reports}),37")
s=s.replace("   self.assertEqual(len(r['sectors']),52);", "   if r['id'].startswith('ngf-'):\n    self.assertEqual(r['sectors'],[]);self.assertNotIn('gdp_per_capita',r);self.assertNotIn('population',r);self.assertIn('unspecified',r['basis']);continue\n   self.assertEqual(len(r['sectors']),52);")
p.write_text(s)
