from pathlib import Path
p=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/index.html');s=p.read_text(encoding='utf-8-sig');s=s.replace('<main><div class="notice">','<main><p><a href="/field-preview/android/">Android test APK and instructions</a></p><div class="notice">',1);p.write_text(s,encoding='utf8')
