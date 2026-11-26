#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
marker='rimalab-startup-observer-scope-fix-v39'
if marker in h: raise SystemExit('V39_FAIL: patch already applied')
# v38 widened this observer from direct children to the entire #bp subtree.
# decorateCatalog() mutates descendants and updateCounts() rewrites innerHTML,
# so observing descendants causes a self-triggering MutationObserver loop.
old="new MutationObserver(()=>{decorateCatalog();installTools()}).observe(root,{childList:true,subtree:true});"
new="new MutationObserver(()=>{decorateCatalog();installTools()}).observe(root,{childList:true,subtree:false});"
if h.count(old)!=1: raise SystemExit(f'V39_FAIL: expected one recursive #bp observer, found {h.count(old)}')
h=h.replace(old,new,1)
guard=r'''<script id="rimalab-startup-observer-scope-fix-v39">
(function(){
 'use strict';
 const root=document.getElementById('bp');
 if(!root||!window.MutationObserver)return;
 window.__rimaStartupObserverScope='direct-children-only';
})();
</script>
'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V39_FAIL: </body> not found')
h=h[:pos]+guard+h[pos:]
g=gp.read_text(encoding='utf-8')
m=re.search(r'\bversionCode\s+(\d+)',g)
if not m: raise SystemExit('V39_FAIL: versionCode missing')
if int(m.group(1))>=59: raise SystemExit('V39_FAIL: versionCode already >=59')
g=g[:m.start(1)]+'59'+g[m.end(1):]
m=re.search(r"""versionName\s+['"]([^'"]+)['"]""",g)
if not m: raise SystemExit('V39_FAIL: versionName missing')
g=g[:m.start(1)]+'3.1.7'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V39_OK: corrigido loop infinito do observer do catálogo; version 3.1.7')
