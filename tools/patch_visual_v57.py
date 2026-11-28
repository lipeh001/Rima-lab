#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V57_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-startup-unfreeze-v57' in h: raise SystemExit('V57_FAIL: patch repetido')
h,n=re.subn(r'<script id="rimalab-centered-heart-runtime-v56">[\s\S]*?</script>\s*','',h,count=1)
if n!=1: raise SystemExit('V57_FAIL: V56 observer script missing or duplicated')
for pat in [r'\.rima-heart-host\{[^}]*\}\s*',r'\.rima-heart-icon\{[^}]*\}\s*',r'\.rima-heart-icon path\{[^}]*\}\s*',r'\.rima-heart-icon\[data-filled="true"\] path\{[^}]*\}\s*']:
 h=re.sub(pat,'',h,count=1)
guard='''<script id="rimalab-startup-unfreeze-v57">
(function(){
 'use strict';
 // Favorites remain managed by the existing V54 event/state system.
 // No global MutationObserver, polling, or DOM-wide scanning is installed here.
 window.__rimaStartupUnfreeze='v57-v54-favorites-native';
})();
</script>
'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V57_FAIL: </body> ausente')
h=h[:pos]+guard+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='76': raise SystemExit('V57_FAIL: versionCode base não é 76')
g=g[:m.start(1)]+'77'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.3.4': raise SystemExit('V57_FAIL: versionName base não é 3.3.4')
g=g[:m.start(1)]+'3.3.5'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V57_OK: removed V56 global observer; restored V54 heart state system; version 3.3.5/code77')
