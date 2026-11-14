NSIPA PBMS — current release, 14 November 2026

Read the repository README and docs/current/INSTALLATION.md before deployment.
The current programme-to-disbursement flow uses native Odoo addon nsipa_approval,
not a browser-only demo. The addon and registry/AWE schema patches are required.
Build: npm ci; npm run build. Source is under src/ and nsipa_approval/.
Frontend entry: /pbms-ui/#programme-flow. /web?native=1 is administrative recovery.
Programme Admin -> Payment submission -> Finance -> Audit -> CEO -> Admin XLS.
The final export does not dispatch payments. Existing legacy payment flows remain separate.
Keep existing NSIPA logo with words; sections marked for later removal are retained.
Install with ../release/install_pbms.py --help after provisioning the base platform.
Do not execute environment-specific test or fixture scripts as an installation sequence.
