#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V51_FAIL: missing HTML or Gradle')
h=hp.read_text(encoding='utf-8'); g=gp.read_text(encoding='utf-8')
if 'rimalab-player-stage-gate-v51' in h: raise SystemExit('V51_FAIL: already applied')
if 'rimalab-selector-favorites-sync-v42' not in h or 'rimalab-shared-selector-orientation-runtime-v49' not in h:
 raise SystemExit('V51_FAIL: expected V42/V49 runtime missing')

# V42 currently docks the player on every landscape rotation, including setup.
# Only apply dock geometry while the live training stage AND actual audio are active.
tag='<script id="rimalab-selector-favorites-sync-v42">'
a=h.find(tag)
if a<0: raise SystemExit('V51_FAIL: V42 runtime missing')
b=a+len(tag); z=h.find('</script>',b); js=h[b:z]
old=""" function dockPlayer(){
  const bar=$('#pbar');if(!bar)return;
  const landscape=(window.matchMedia&&window.matchMedia('(orientation:landscape)').matches)||window.innerWidth>window.innerHeight;
  if(!landscape)return;
  const set=(k,v)=>bar.style.setProperty(k,v,'important');"""
new=""" function dockPlayer(){
  const bar=$('#pbar');if(!bar)return;
  const landscape=(window.matchMedia&&window.matchMedia('(orientation:landscape)').matches)||window.innerWidth>window.innerHeight;
  const live=!!(document.getElementById('lv')&&!document.getElementById('lv').hidden&&document.body.classList.contains('pl')&&!document.body.classList.contains('pv'));
  const playing=document.body.classList.contains('rima-player-visible');
  if(!landscape||!live||!playing){
   ['position','top','bottom','left','right','inset','transform','z-index','width','max-width','height','min-height','max-height'].forEach(k=>bar.style.removeProperty(k));
   return;
  }
  const set=(k,v)=>bar.style.setProperty(k,v,'important');"""
if old not in js: raise SystemExit('V51_FAIL: V42 dockPlayer function not found')
js=js.replace(old,new,1)
h=h[:b]+js+h[z:]

css=r"""
<style id="rimalab-player-stage-gate-v51">
/* The persistent player is unavailable during setup, including step 1 and step 2.
   It becomes visible only after audio is active inside the live training stage. */
body:not(.rima-v51-player-eligible) #pbar{display:none!important;visibility:hidden!important;pointer-events:none!important}
body.rima-v51-player-eligible #pbar{display:flex!important;visibility:visible!important;pointer-events:auto!important}
body:not(.rima-v51-player-eligible) #pbar *{pointer-events:none!important}
</style>
<script id="rimalab-player-stage-gate-runtime-v51">
(function(){
 'use strict';
 const body=document.body,lv=document.getElementById('lv'),bar=document.getElementById('pbar');
 if(!bar||!lv)return;
 const dock=['position','top','bottom','left','right','inset','transform','z-index','width','max-width','height','min-height','max-height'];
 function landscape(){return !!(window.matchMedia&&window.matchMedia('(orientation:landscape)').matches)||innerWidth>innerHeight}
 function sync(){
  const live=!lv.hidden&&body.classList.contains('pl')&&!body.classList.contains('pv');
  const audio=body.classList.contains('rima-player-visible');
  const eligible=live&&audio;
  body.classList.toggle('rima-v51-player-eligible',eligible);
  if(!eligible){
   dock.forEach(k=>bar.style.removeProperty(k));
   bar.style.setProperty('display','none','important');
   bar.style.setProperty('visibility','hidden','important');
   bar.style.setProperty('pointer-events','none','important');
   return;
  }
  bar.style.removeProperty('display');bar.style.removeProperty('visibility');bar.style.removeProperty('pointer-events');
  if(landscape()&&typeof window.rimaV42DockPlayer==='function')window.rimaV42DockPlayer();
 }
 function settle(){requestAnimationFrame(sync);setTimeout(sync,100);setTimeout(sync,300)}
 if(window.MutationObserver){
  new MutationObserver(settle).observe(body,{attributes:true,attributeFilter:['class']});
  new MutationObserver(settle).observe(lv,{attributes:true,attributeFilter:['hidden','class']});
 }
 window.addEventListener('resize',settle,{passive:true});
 window.addEventListener('orientationchange',settle,{passive:true});
 window.addEventListener('pageshow',settle,{passive:true});
 if(window.visualViewport)window.visualViewport.addEventListener('resize',settle,{passive:true});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)settle()});
 settle();window.rimaV51SyncPlayer=sync;
})();
</script>
"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V51_FAIL: body close missing')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='71': raise SystemExit('V51_FAIL: expected base code 71')
g=g[:m.start()]+re.sub('71','72',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.2.9': raise SystemExit('V51_FAIL: expected base version 3.2.9')
g=g[:m.start()]+m.group(0).replace('3.2.9','3.3.0')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V51_OK: hide player in setup and inactive stages; show only for active audio inside live stage; clear landscape dock geometry outside stage; version 3.3.0/code72')
