from pathlib import Path
p=Path(__file__).with_name('build_report.py');s=p.read_text(encoding='utf-8')
old='The original four controlled imports and four further automatic imports passed across both domain families using the existing review APIs. Physical Android behavior remains unverified; no device was connected and the video is illustrative. NPC attestation, the final GPS policy and hosting/interbank readiness still need confirmation. Automatic ODK-to-intake synchronization is now enabled every minute while the host is running; registry ingestion still requires both reviewers. Any other historical numeric source needs its own published dictionary.'
new='Automatic synchronization is enabled; both reviewers remain mandatory. Physical Android testing, NPC attestation, the final GPS policy and hosting/interbank readiness remain open. Other source forms need verified mappings. The video remains illustrative.'
assert old in s;s=s.replace(old,new)
anchor="section('What is needed for the remaining tests',["
insert="""p('Automatic-import record references','SubNS')
auto_checks=json.loads((work/'auto-sync-verification/final-checks.json').read_text())
for item in auto_checks['checks']:
 if 'functional_id' in item:p(html.escape(item['case'])+' | '+html.escape(item['functional_id'])+' | One intake, one registry record; saved fields verified.')
p('Final ledger: eight submitted sources (four previous imports reconciled plus four new scheduled imports); seven held sources (five older form versions plus two deliberate invalid-code tests). Latest verified pass had zero transient failures. The timer remained enabled and active after restart.')
"""
s=s.replace(anchor,insert+'\n'+anchor)
s=s.replace('NSIPA-Client-Feedback-Report-Automatic-Sync-Verified.pdf','NSIPA-Client-Feedback-Report-Automatic-Sync.pdf')
p.write_text(s,encoding='utf-8')
