#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export LC_ALL=C TZ=UTC
ANDROID=/usr/lib/android-sdk/platforms/android-23/android.jar
R8=/opt/ng2p-android-tools/r8.jar
KEYSTORE=${DEMO_KEYSTORE:-$HOME/.android/ng2p-demo.keystore}
# Reuse the existing demo key. Never silently generate a different identity.
test -f "$KEYSTORE"
rm -rf build/classes build/gen
mkdir -p build/classes build/gen
/usr/bin/aapt package -f -m -M AndroidManifest.xml -S res -A assets -I "$ANDROID" -F build/unsigned.apk -J build/gen
javac -encoding UTF-8 -source 8 -target 8 -classpath "$ANDROID" -d build/classes src/org/nigeriag2p/field/*.java build/gen/org/nigeriag2p/field/R.java
python3 reproducible_zip.py classes build/classes build/classes.jar
java -cp "$R8" com.android.tools.r8.D8 --min-api 23 --lib "$ANDROID" --output build build/classes.jar
python3 reproducible_zip.py apk build/unsigned.apk build/classes.dex
zipalign -f 4 build/unsigned.apk build/aligned.apk
apksigner sign --ks "$KEYSTORE" --ks-pass pass:android --key-pass pass:android --out build/nigeria-g2p-field-demo.apk build/aligned.apk
apksigner verify --verbose --print-certs build/nigeria-g2p-field-demo.apk
sha256sum build/nigeria-g2p-field-demo.apk
