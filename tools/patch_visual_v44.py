#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V44_FAIL: missing app assets or Gradle file')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-favorites-catalog-lexical-v44' in h: raise SystemExit('V44_FAIL: already applied')
if 'rimalab-favorites-layout-runtime-v43' not in h: raise SystemExit('V44_FAIL: V43 Favorites runtime missing')
old="const catalog=()=>window.ZLIB||{};"
new="const catalog=()=>typeof ZLIB!=='undefined'&&ZLIB?ZLIB:(window.ZLIB||{});"
if h.count(old)!=1: raise SystemExit('V44_FAIL: expected exactly one broken V43 catalog resolver; found '+str(h.count(old)))
h=h.replace(old,new,1)
if "const KEY='rimalab_favorites_v29'" not in h: raise SystemExit('V44_FAIL: original favorites storage key missing')
if "localStorage.removeItem('rimalab_favorites_v29')" in h: raise SystemExit('V44_FAIL: unexpected destructive favorites migration')
style=r'''<style id="rimalab-favorites-catalog-lexical-v44">
#bp>.rima-v43-favlist,#bq>.rima-v43-favlist{display:block!important;visibility:visible!important;opacity:1!important}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row{pointer-events:auto!important}
#bp .rima-v43-fav-play,#bp .rima-v43-fav-heart,#bq .rima-v43-fav-play,#bq .rima-v43-fav-heart{pointer-events:auto!important;touch-action:manipulation!important}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V44_FAIL: body close missing')
h=h[:pos]+style+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='63': raise SystemExit('V44_FAIL: expected versionCode 63')
g=g[:m.start()]+re.sub('63','64',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.1': raise SystemExit('V44_FAIL: expected versionName 3.2.1')
g=g[:m.start()]+m.group(0).replace('3.2.1','3.2.2')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V44_OK: Favorites uses lexical ZLIB with safe window fallback; existing favorites preserved; 3.2.2/code64')
