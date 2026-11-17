# Enumerator mobile app downloads

Updated 17 November 2026.

After signing in as a field agent, select **Mobile app downloads & setup** on the Registry overview, or open https://g2p-register.wverve.in/en/offline.

Two download cards are displayed together:

- **NSIPA Household Intake v0.7** — our Android demonstration APK, with installation and sample upload instructions. Use fictional household data. This test build is separate from authenticated native registry collection; its sample upload configuration and demonstration supervisor PIN do not provide registry staff authentication.
- **ODK Collect** — the official Google Play installation link and installation instructions. Connect this app to the registry with the field agent's private setup QR on the same page. Keep that QR private.

Links:

- NSIPA APK: https://g2p.wverve.in/field-preview/android/nsipa-household-intake-v0.7.apk
- NSIPA instructions: https://g2p.wverve.in/field-preview/android/
- ODK Collect: https://play.google.com/store/apps/details?id=org.odk.collect.android
- ODK instructions: https://docs.getodk.org/collect-install/

The two cards use the existing intake-edit permission. This change grants no new record, review or staff-administration permissions. The existing QR setup endpoint and registry review flow are unchanged. Shared presentation branding preserves the ODK Collect product name.

## Source and deployment

The dashboard and download screen are `registry-ui-source/src/app/[locale]/page.tsx` and `registry-ui-source/src/app/[locale]/offline/page.tsx`. Shared branding is `branding/iqs-brand.js`.

Build the registry UI with `docker build -f Dockerfile.native -t nsipa/master-registry:mobile-downloads-20261117 .` from `registry-ui-source/`. Follow the existing installation guide for destination configuration and deployment. Publish the updated branding script through the existing branding asset mount.

Original sandbox deployment: registry UI image `nsipa/master-registry:mobile-downloads-20261117`.

## Validation

- Production build and TypeScript completed successfully.
- Kubernetes rollout completed successfully.
- An actual field-agent browser login reached the new dashboard shortcut and both download links.
- Private ODK QR setup control remained available; no QR was generated for the verification report.
- Desktop and 390-pixel phone layouts were reviewed; no horizontal overflow was detected.
- NSIPA v0.7 APK download returned HTTP 200.

No physical-device installation, offline capture or upload acceptance test was performed for this UI-only change.
