from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
main=root/'app/src/main/java/app/rimalab/MainActivity.java'
manifest=root/'app/src/main/AndroidManifest.xml'
print('===NATIVE_SOURCE_INSPECTION===')
if manifest.exists():
    txt=manifest.read_text(encoding='utf-8')
    print('---MANIFEST PERMISSIONS---')
    for line in txt.splitlines():
        if 'uses-permission' in line or 'uses-feature' in line or 'application' in line:
            print(line[:400])
if main.exists():
    lines=main.read_text(encoding='utf-8').splitlines()
    hits=[i for i,x in enumerate(lines) if re.search(r'WebView|WebChrome|PermissionRequest|onPermissionRequest|setWebChromeClient|setWebViewClient|loadUrl|JavascriptInterface|RimaBridge',x)]
    selected=set()
    for i in hits:
        selected.update(range(max(0,i-5),min(len(lines),i+9)))
    print('---MAIN ACTIVITY WEBVIEW/PERMISSION CONTEXT---')
    last=-2
    for i in sorted(selected):
        if i>last+1: print('...')
        print(f'{i+1}: {lines[i][:500]}')
        last=i
else: print('MainActivity.java not found')
print('===END_NATIVE_SOURCE_INSPECTION===')
