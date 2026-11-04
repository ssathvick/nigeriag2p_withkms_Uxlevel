# Nigeria G2P Field — emulator demonstration

This APK is a sample-only prototype. Never enter real household data or use it for operational approvals.

Install the signed debug/demo APK on Android 6.0 (API 23) or newer using `adb install -r nigeria-g2p-field-demo.apk`. It is not signed for production distribution.

1. Create a fictional visit and save a draft. Enter consent and complete each section.
2. On Review, save and open supervisor review. The demonstration PIN is 246810. This PIN is hard-coded and is NOT an authenticated staff identity or a secure approval control.
3. An approved demo record remains on the device. Sync settings accepts an HTTPS ODK Central App User project URL; the sample form `nsipa_field_household_demo` must be published in that project. Approved sample records are queued for a network-constrained Android background job; use Retry upload to request an additional attempt.
4. The app reports a successful upload only on HTTP 201. A failed attempt leaves the record for manual retry. The device encrypts the record store and connection URL using Android Keystore, and disables application backup. The app requests an upload when a record is approved, and schedules periodic retry. Android controls timing and may delay background work. The user can refresh the workspace to check the status.

The demonstration form is a fixed form implemented in native Java, not a general ODK Collect or XForms interpreter. A sample-only ODK project and OnePlus test App User are configured; the offline-to-online sample upload has been verified on that device. Uploaded `review_confirmation` means demo confirmation only and does not prove the identity of an authorized supervisor. A production release requires server-issued device enrollment, independently authenticated offline supervisors with expiry/revocation and separation of duties, signed auditable approvals, conflict/idempotency handling, production-grade durable retry and conflict handling, full security review, a supported Android build configuration and device/emulator testing.

Build on Ubuntu with the Debian Android SDK build-tools/platform-23 packages, JDK 17 and R8 at `/opt/ng2p-android-tools/r8.jar`: `bash build.sh`. The script uses a locally generated test signing key.

## Location reference and coordinates

The offline pickers use Open Admin Data, Nigeria Administrative Divisions, https://github.com/open-admin-data/nigeria-administrative-divisions, CC BY 4.0, retrieved 4 November 2026. Bundled snapshot: 37 states/FCT, 774 LGAs and 8,799 wards. Source identifiers are catalogue identifiers, not asserted official P-codes. This is reference data, not a validated national gazetteer; review coverage and names with the relevant authorities before field use. A parent change clears dependent choices, and previously entered free-text areas must be reselected.

Location access is requested only when the user chooses device GPS. Coordinates can instead be entered manually; both must be present and within global latitude/longitude ranges. The Google Maps link opens the captured or entered coordinates; it does not determine or validate the selected state, LGA or ward. Maps may require an internet connection. The app writes coordinates to the sample ODK geopoint when they are supplied.

The Android UI and offline sample flow were tested on the OnePlus; GPS permission, location capture and Google Maps handoff remain untested. The catalogue parent relationships were checked.

Other devices require their own appropriate App User configuration and testing.

## OnePlus 12 device test, 4 November 2026

Version 0.4 was installed and launched. A fictional draft was entered using Plateau / Jos North / Gangare, saved, and reopened. On the review screen an incorrect test PIN was rejected. With Wi-Fi off and mobile data already off, the shared demonstration PIN finalized the sample to `approved-demo`; Wi-Fi was then restored. The system registered the upload job. This verifies only the demo PIN flow; it does not authenticate a separate supervisor. ODK Central project 1 was created for samples, but form publication, App User provisioning, and an actual device-to-server upload remained pending at the time of this test.

## Server receipt, 4 November 2026

The isolated sample ODK project and form were configured with a project-scoped OnePlus App User. The previously offline-approved fictional record SAMPLE-JOS-01 was automatically uploaded after the test connection was configured while online. ODK Central showed one submission from that App User in Received state, and the app showed sent. A separate test of approving a new record offline with the connection already configured and then reconnecting was not completed; the phone disconnected during that test. The shared demo PIN remains unauthenticated.

## Offline reconnection test, 4 November 2026

With the project URL already configured, the OnePlus 12 finalized SAMPLE-RECONNECT-03 using the shared demo PIN while Wi-Fi and mobile data were disabled and Android reported no active default network. ODK had zero matching submissions before Wi-Fi was restored. Without a manual retry, ODK then received exactly one matching submission and the refreshed phone workspace showed sent. The server payload matched the fictional area, household counts and demo review confirmation. Supervisor identity is not authenticated; this remains a sample-only app.
