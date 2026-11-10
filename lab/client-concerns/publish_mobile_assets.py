from pathlib import Path
import shutil
src=Path(__file__).resolve().parents[1];root=Path('/opt/openg2p-lab')
for home in ['home','public-home']:
 target=root/home/'field-preview/android';target.mkdir(parents=True,exist_ok=True)
 for name in ['nsipa-household-intake-v0.7.apk','nigeria-g2p-field-demo.apk']:
  shutil.copy2(src/'field-app/android/build/nigeria-g2p-field-demo.apk',target/name);(target/name).chmod(0o644)
shutil.copy2(src/'registration-ui/geo-form.js',root/'registration/static/geo-form.js')
shutil.copy2(src/'registration-ui/profile.html',root/'registration/templates/profile.html')
print('Published NSIPA v0.7 APK, compatible existing download URL, browser GPS and profile link')
