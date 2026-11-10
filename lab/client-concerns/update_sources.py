from pathlib import Path
root=Path(__file__).parent.parent
p=root/'persona-ui/src/main.jsx';s=p.read_text();s=s.replace('<p>{profile.reason}</p></div>','<p>{profile.reason}</p>{profile.review_history?.[0]&&<p>Reviewer: {profile.review_history[0].actor_name} · {new Date(profile.review_history[0].at).toLocaleString()}</p>}</div>')
s=s.replace('<div className="journey">','{profile.review_history?.length>0&&<details className="review-history"><summary>Review history</summary>{profile.review_history.map((item,i)=><p key={i}><strong>{item.actor_name}</strong> · {item.action===\'reject\'?\'Returned for correction\':item.action} · {new Date(item.at).toLocaleString()}<br/>{item.reason}</p>)}</details>}<div className="journey">');p.write_text(s)
# Replace known terminology in the current translation source, not technical database identifiers.
p=root/'field-app/build_form.py';s=p.read_text().replace('NSIPA Field Household — Sample','Household Intake Form');p.write_text(s)
p=root/'field-app/android/src/org/nigeriag2p/field/MainActivity.java';s=p.read_text().replace('Nigeria G2P field app demo.','NSIPA Household Intake Form.').replace('Nigeria G2P','NSIPA Unified G2P');p.write_text(s)
print('Workspace review provenance and field form display title updated.')
