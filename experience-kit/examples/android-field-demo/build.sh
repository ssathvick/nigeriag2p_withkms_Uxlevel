set -euo pipefail
cd "$(dirname "$0")"
rm -rf build/classes build/gen
mkdir -p build/classes build/gen
sed -i '1s/^\xEF\xBB\xBF//' src/org/nigeriag2p/field/*.java
ANDROID=/usr/lib/android-sdk/platforms/android-23/android.jar
/usr/bin/aapt package -f -m -M AndroidManifest.xml -S res -A assets -I "$ANDROID" -F build/unsigned.apk -J build/gen
javac -encoding UTF-8 -source 8 -target 8 -classpath "$ANDROID" -d build/classes src/org/nigeriag2p/field/*.java build/gen/org/nigeriag2p/field/R.java
jar cf build/classes.jar -C build/classes .
java -cp /opt/ng2p-android-tools/r8.jar com.android.tools.r8.D8 --min-api 23 --lib "$ANDROID" --output build build/classes.jar
cd build
zip -q unsigned.apk classes.dex
zipalign -f 4 unsigned.apk aligned.apk
if [ ! -f "$HOME/.android/ng2p-demo.keystore" ]; then mkdir -p "$HOME/.android"; keytool -genkeypair -keystore "$HOME/.android/ng2p-demo.keystore" -storepass android -keypass android -alias demo -dname 'CN=Nigeria G2P Emulator Demo' -keyalg RSA -keysize 2048 -validity 3650 >/dev/null 2>&1; fi
apksigner sign --ks "$HOME/.android/ng2p-demo.keystore" --ks-pass pass:android --key-pass pass:android --out nigeria-g2p-field-demo.apk aligned.apk
apksigner verify --verbose nigeria-g2p-field-demo.apk
