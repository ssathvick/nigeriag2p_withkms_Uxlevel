from pathlib import Path
p=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android/README.md')
s=p.read_text(encoding='utf8')
s+='\n## OnePlus 12 device test, 4 November 2026\n\nVersion 0.4 was installed and launched. A fictional draft was entered using Plateau / Jos North / Gangare, saved, and reopened. On the review screen an incorrect test PIN was rejected. With Wi-Fi off and mobile data already off, the shared demonstration PIN finalized the sample to `approved-demo`; Wi-Fi was then restored. The system registered the upload job. This verifies only the demo PIN flow; it does not authenticate a separate supervisor. ODK Central project 1 was created for samples, but form publication, App User provisioning, and an actual device-to-server upload remained pending at the time of this test.\n'
p.write_text(s,encoding='utf8')
