import pathlib,json,secrets,tarfile,subprocess,hashlib,os,shutil
meta=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/tmp/current-private-backup.json').read_text(encoding='utf-8-sig'));stamp=meta['stamp']
root=pathlib.Path('/opt/openg2p-private-backups')/stamp;dest=pathlib.Path('/mnt/d/NigeriaG2P-Backups')/stamp;keydir=pathlib.Path('/mnt/e/NigeriaG2P-Recovery-Keys')/stamp;key=keydir/'recovery-key.txt';os.umask(0o077)
v=json.loads((root/'verification.json').read_text());assert v['status']=='passed';assert not json.loads((root/'resume-report.json').read_text())['errors']
if not key.exists():key.write_text(secrets.token_urlsafe(64)+'\n')
assert len(key.read_text().strip())>=80
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while x:=f.read(4*1024*1024):h.update(x)
 return h.hexdigest()
manifest=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in root.rglob('*') if p.is_file()]
(root/'MANIFEST.json').write_text(json.dumps(manifest,indent=2))
archive=root.parent/(stamp+'.tar.gz')
with tarfile.open(archive,'w:gz') as t:t.add(root,arcname='nsipa-runtime-backup')
expected=sha(archive);encrypted=dest/'nsipa-databases-runtime.tar.gz.gpg'
gpg=['gpg','--batch','--pinentry-mode','loopback','--passphrase-file',str(key)]
subprocess.run(gpg+['--symmetric','--cipher-algo','AES256','--s2k-digest-algo','SHA512','--s2k-count','65011712','--compress-algo','none','--output',str(encrypted),str(archive)],check=True,capture_output=True)
p=subprocess.Popen(gpg+['--decrypt',str(encrypted)],stdout=subprocess.PIPE,stderr=subprocess.PIPE);h=hashlib.sha256()
while x:=p.stdout.read(4*1024*1024):h.update(x)
err=p.stderr.read();assert p.wait()==0,'Decryption failed';assert h.hexdigest()==expected,'Decrypted archive mismatch'
summary={'status':'passed','stamp':stamp,'encrypted_archive':encrypted.name,'cipher':'GPG AES256 symmetric encryption with integrity checking','encrypted_sha256':sha(encrypted),'encrypted_bytes':encrypted.stat().st_size,'decrypted_sha256':expected,'decrypt_byte_comparison':'passed','postgresql':v['postgresql'],'sqlite':v['sqlite'],'redis':v.get('redis',{}),'file_archives':v['archives'],'recovery_key_location':str(key),'scope':'Project databases and runtime configuration/file volumes; not a full WSL operating-system image','restore_test':'PostgreSQL restored into isolated disposable pods with table row-count comparison; SQLite integrity and Redis RDB format/checksum checks; archives read to end','plaintext_cleanup':'pending'}
(dest/'Verification-Summary.json').write_text(json.dumps(summary,indent=2));(dest/'SHA256SUMS.txt').write_text(summary['encrypted_sha256']+'  '+encrypted.name+'\n')
print('Encrypted archive decrypted successfully and matched the verified plaintext byte-for-byte',flush=True)
# Remove only the newly created, verified staging paths, never live runtime paths.
assert root.parent==pathlib.Path('/opt/openg2p-private-backups') and root.name==stamp and archive.parent==root.parent
shutil.rmtree(root);archive.unlink();summary['plaintext_cleanup']='completed';(dest/'Verification-Summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({'encrypted_bytes':summary['encrypted_bytes'],'postgresql_services':len(v['postgresql']),'sqlite_databases':len(v['sqlite']),'redis_snapshots':len(v.get('redis',{})),'plaintext_cleanup':'completed'}),flush=True)
