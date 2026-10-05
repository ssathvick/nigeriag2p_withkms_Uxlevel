# Backup and recovery

GitHub preserves the cleaned source. It does not contain the operational databases,
household records, credentials, TLS private keys, tunnel credentials or Ollama models.

The separate 5 October 2026 recovery set includes:

* An offline WSL export of the installed Linux environment, including K3s volumes,
  container images, system configuration and the local AI model.
* Logical backups of five PostgreSQL services, Kubernetes configuration and the
  registration SQLite database, which also stores knowledge management state.
* Windows application sources, BMAD project files and project documents.

The WSL export was imported into an isolated temporary distribution with systemd
disabled. Registration/K3s SQLite integrity and Ollama model blob hashes were checked.
All five PostgreSQL logical dumps were independently restored into disposable pods;
COPY row counts were checked across 1,390 tables. Application services were not
started in the recovery clone. This is not a clean-machine end-to-end deployment test.

The archives use AES-256 GPG encryption. The recovery key belongs in secure storage
separate from the backup and must not be committed here. Keep an off-machine copy of
both, in separate secure locations. The private backup folder includes its recovery
guide and hash/verification reports.

## Source checks

* Checksum-verified Gitleaks scanned the source tree with no findings.
* An additional scan checked against current runtime secret values without
  recording those values in this repository.
* Python source syntax and the context-help mapping checks passed.

## Restore precautions

Recover into a new directory/distribution. Do not overwrite the working installation.
The export intentionally has systemd disabled to prevent duplicate application and
Cloudflare services from starting during inspection. Enable services only after
the original host is offline or the recovered installation has distinct networking,
domains and tunnel credentials. The private recovery guide gives the exact commands.
