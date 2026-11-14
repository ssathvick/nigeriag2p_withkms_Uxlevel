from pathlib import Path
p=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android/README.md')
s=p.read_text(encoding='utf8')
s=s.replace('Then manually send an approved sample.','Approved sample records are queued for a network-constrained Android background job; use Retry upload to request an additional attempt.')
s=s.replace('The device encrypts the record store and connection URL using Android Keystore, and disables application backup. It does not perform background sync.','The device encrypts the record store and connection URL using Android Keystore, and disables application backup. The app requests an upload when a record is approved, and schedules periodic retry. Android controls timing and may delay background work. The user can refresh the workspace to check the status.')
s=s.replace('automatic durable retry, full security review','production-grade durable retry and conflict handling, full security review')
s+='\nVersion 0.3 was installed on a connected OnePlus 12 and launched. Complete UI, offline/reconnect and server upload tests have not been completed. A valid App User URL and published test form are still required.\n'
p.write_text(s,encoding='utf8')
