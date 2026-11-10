from pathlib import Path
p=Path(__file__).with_name('build_report.py');s=p.read_text(encoding='utf-8-sig')
changes={
'Only the two deliberate invalid-code samples remain held.':'Both negative-code fixtures are now closed as excluded tests; validation is unchanged.',
'Only the two invalid numeric tests remain quarantined, with no intake created.':'The two invalid numeric tests have now been reviewed and closed as EXCLUDED_TEST, with no intake created; see the invalid-code review section.',
'two deliberate invalid-code tests remain held.':'two deliberate invalid-code tests are closed as EXCLUDED_TEST, with zero active quarantines.',
'The two intentional numeric-code failure tests remain quarantined; they were not silently repaired or imported.':'The two intentional numeric-code failure tests have been closed as excluded test fixtures; they were not repaired or imported.'
}
for old,new in changes.items():
 assert old in s,old;s=s.replace(old,new)
anchor="section('What is needed for the remaining tests',["
addition="""
section('Two invalid-code submissions: resolved',[
('Source review','Proven negative tests','Both submissions are deliberate synthetic copies created by verify-sync-replay.cjs. The script copied the already imported Chuka Obi numeric-form source, assigned a new instance ID and replaced roof_material 2 with 999. Both stored XML documents exactly match those transformations, byte for byte. They do not represent two additional households.'),
('Dictionary and validation','Unchanged','The published choice list maps code 2 to Corrugated iron and contains no code 999. Four authenticated source checks across both ODK domains confirmed the test provenance and continued rejection of 999. No mapping from 999 to a real roof type was added, and no required-field, consent, version or approval rule was relaxed.'),
('Safe resolution','Closed as EXCLUDED_TEST','Classified only these two reviewed source instances as excluded test fixtures. Preserved the original XML, source hashes, earlier quarantine reasons and resolution audit. No source value was edited; no intake, approval request or registry record was created. Correcting and importing these cloned tests would duplicate the existing synthetic household.'),
('Cross-domain and scheduled checks','Passed','Both registry domains returned record-not-found for each excluded instance: four absence checks. The original valid source remained present exactly once with CORRUGATED_IRON on both domains: two control checks. A subsequent scheduled pass reported thirteen submitted sources, two excluded tests, zero active quarantines and zero transient failures. Automatic synchronization remains active.'),
('Repeat protection and evidence','Passed','Eight worker regression tests passed, including repeated delivery of an excluded fixture without import and a changed excluded source returning to SOURCE_CHANGED for review. Code 999 remains invalid. Evidence is in invalid-code-review/: source-review.json, resolution-audit.json, domain-checks.json, final-checks.json and worker-tests.log. A private pre-change ledger and worker backup are retained under /opt/openg2p-lab/odk-sync/invalid-code-review/.')])
p('Reviewed source instances','SubNS')
for item in json.loads((work/'invalid-code-review/final-checks.json').read_text())['checks']:
 p(html.escape(item['instance'])+'<br/>EXCLUDED_TEST | Zero intakes | Zero registry records | Original source preserved')
p('No further client correction is needed for these two deliberate test fixtures. A real submission with an unknown code would still require reliable source correction and the normal two-reviewer workflow.')
"""
assert anchor in s;s=s.replace(anchor,addition+'\n'+anchor)
s=s.replace('NSIPA-Client-Feedback-Report-Legacy-Imports-Verified.pdf','NSIPA-Client-Feedback-Report-Invalid-Code-Review.pdf')
p.write_text(s,encoding='utf-8')
