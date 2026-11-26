#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
if 'rimalab-startup-observer-loop-guard-v38' in h: raise SystemExit('V38_FAIL: already applied')
def put(sid,body):
 global h
 pat=r'(<script id="'+re.escape(sid)+r'">)(.*?)(</script>)'
 h,n=re.subn(pat,lambda m:m.group(1)+'\n'+body+'\n'+m.group(3),h,count=1,flags=re.S)
 if n!=1: raise SystemExit('V38_FAIL: missing '+sid)
put('rimalab-mode-config-runtime-v30',"""
(function(){
 'use strict';
 const $=s=>document.querySelector(s);
 function txt(el,v){if(el&&el.textContent!==v)el.textContent=v}
 function arrange(){
  const step=$('#train-step-2');if(!step)return;
  const heading=step.querySelector('.stp'),banner=$('#rima-v29-mode-banner'),toggle=$('#rima-v29-mode-toggle'),list=$('#rima-v29-mode-list'),dfw=$('#dfw'),bp=$('#bp');
  if(heading)txt(heading.querySelector('h2'),'Escolha o modo');
  if(banner&&heading&&banner.previousElementSibling!==heading)heading.insertAdjacentElement('afterend',banner);
  if(banner&&toggle&&banner.nextElementSibling!==toggle)banner.insertAdjacentElement('afterend',toggle);
  if(toggle&&list&&toggle.nextElementSibling!==list)toggle.insertAdjacentElement('afterend',list);
  if(dfw){txt(dfw.querySelector('.stp .n'),'2');txt(dfw.querySelector('.stp h2'),'Dificuldade')}
  if(bp){const hd=bp.previousElementSibling;if(hd&&hd.classList.contains('stp')){txt(hd.querySelector('.n'),'3');txt(hd.querySelector('h2'),'Escolha o beat')}}
  if(list){const height=list.classList.contains('open')?'2000px':'0';if(list.style.maxHeight!==height)list.style.maxHeight=height;if(list.style.overflow!=='visible')list.style.overflow='visible'}
 }
 let pending=false;
 function schedule(){if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;arrange()})}
 function init(){
  arrange();
  document.addEventListener('click',e=>{if(e.target.closest('#rima-v29-mode-toggle,#rima-v29-mode-list [data-mode]'))schedule()},true);
  window.addEventListener('resize',schedule,{passive:true});
  const old=window.trainNext;
  if(typeof old==='function'&&!old.__rimaV38){const f=function(){const r=old.apply(this,arguments);schedule();return r};f.__rimaV38=true;window.trainNext=f}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
""")
# Remove the v31 observer that re-enters updateModeUI when #md is mutated.
m=re.search(r'<script id="rimalab-complete-runtime-v31">(.*?)</script>',h,re.S)
if not m: raise SystemExit('V38_FAIL: v31 script missing')
body=m.group(1)
body=body.replace("const modeRoot=$('#md');if(modeRoot)new MutationObserver(()=>{if(!$('#train-step-2')?.hidden)updateModeUI()}).observe(modeRoot,{childList:true,subtree:true});","")
body=body.replace("setInterval(()=>{addPlayerHeart();decorateCatalog();updateCounts()},1500);","")
body=body.replace("new MutationObserver(()=>{decorateCatalog();installTools()}).observe(root,{childList:true,subtree:false});","new MutationObserver(()=>{decorateCatalog();installTools()}).observe(root,{childList:true,subtree:true});")
put('rimalab-complete-runtime-v31',body)
# Remove polling loops. The existing player/catalog callbacks handle state changes.
for sid,old in [('rimalab-player-polish-v33','setInterval(install,1200);'),('rimalab-favorites-inline-v35','setInterval(install,900);')]:
 m=re.search(r'<script id="'+re.escape(sid)+r'">(.*?)</script>',h,re.S)
 if not m: raise SystemExit('V38_FAIL: '+sid+' missing')
 b=m.group(1)
 if old not in b: raise SystemExit('V38_FAIL: polling not found in '+sid)
 b=b.replace(old,'')
 if sid=='rimalab-favorites-inline-v35':
  b=b.replace("function install(){bindPlayer();dock();labels();if(favoritesMode)render();sync()}","function install(){bindPlayer();dock();labels();if(favoritesMode)render();sync()}\nconst oldBar=window.zBarUI;if(typeof oldBar==='function'&&!oldBar.__rimaV38){const f=function(){const r=oldBar.apply(this,arguments);requestAnimationFrame(install);return r};f.__rimaV38=true;window.zBarUI=f}")
 put(sid,b)
# Remove the extra label observer; labels are updated on initial load and mode clicks.
m=re.search(r'<script id="rimalab-mode-number-clean-runtime-v37">(.*?)</script>',h,re.S)
if m:
 b=m.group(1)
 b=re.sub(r"const step=document.getElementById\('train-step-2'\);\s*if\(step\)new MutationObserver\(\(\)=>requestAnimationFrame\(fix\)\)\.observe\(step,\{childList:true,subtree:true\}\);","",b)
 put('rimalab-mode-number-clean-runtime-v37',b)
css="""<style id="rimalab-hide-scrollbar-v38">
html,body,*{scrollbar-width:none!important;-ms-overflow-style:none!important}
::-webkit-scrollbar,*::-webkit-scrollbar{display:none!important;width:0!important;height:0!important;background:transparent!important}
html,body{overscroll-behavior-y:contain}
</style>
"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V38_FAIL: body end')
h=h[:pos]+css+'\n'+h[pos:]
g=gp.read_text(encoding='utf-8')
m=re.search(r'\bversionCode\s+(\d+)',g)
if not m: raise SystemExit('V38_FAIL: versionCode')
g=g[:m.start(1)]+'58'+g[m.end(1):]
m=re.search(r"""versionName\s+['"]([^'"]+)['"]""",g)
if not m: raise SystemExit('V38_FAIL: versionName')
g=g[:m.start(1)]+'3.1.6'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V38_OK: self-triggering observers removed, repeated UI polling removed, scrollbar chrome hidden, version 3.1.6')
