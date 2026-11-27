#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V52_FAIL: HTML or Gradle missing')
h=hp.read_text(encoding='utf-8'); g=gp.read_text(encoding='utf-8')
if 'rimalab-landscape-navigation-touch-v52' in h: raise SystemExit('V52_FAIL: already applied')
if 'rimalab-player-stage-gate-v51' not in h or 'rimalab-shared-selector-orientation-runtime-v49' not in h:
 raise SystemExit('V52_FAIL: expected V49/V51 runtimes missing')
css=r'''<style id="rimalab-landscape-navigation-touch-v52">
/* Landscape setup regression: V36 hid navigation in landscape, while V51
   correctly hid the player outside the live stage. That left no navigation
   and, with V49's fixed main, no usable scroll surface. Restore both. */
@media (orientation:landscape) and (min-width:560px){
 html,body{
  width:100%!important;max-width:100%!important;min-height:100%!important;height:auto!important;
  overflow-x:hidden!important;overflow-y:auto!important;overscroll-behavior-x:none!important;
  overscroll-behavior-y:auto!important;touch-action:pan-y!important;
 }
 body:not(.rima-live-landscape) main{
  position:relative!important;inset:auto!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;
  width:100%!important;max-width:100%!important;height:auto!important;min-height:100vh!important;max-height:none!important;
  margin:0 auto!important;overflow:visible!important;overflow-x:hidden!important;overflow-y:visible!important;
  padding:8px 18px 82px!important;box-sizing:border-box!important;touch-action:pan-y!important;
 }
 body:not(.rima-live-landscape) .tab:not([hidden]),
 body:not(.rima-live-landscape) #ao:not([hidden]),
 body:not(.rima-live-landscape) #su{
  display:block!important;position:relative!important;inset:auto!important;overflow:visible!important;
  width:100%!important;height:auto!important;max-height:none!important;touch-action:pan-y!important;
 }
 body:not(.rima-live-landscape) #su{
  column-count:initial!important;columns:initial!important;
  display:grid!important;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr)!important;
  align-items:start!important;gap:12px!important;
 }
 body:not(.rima-live-landscape) #su>.home-hero{grid-column:1!important;grid-row:1/span 2!important;margin:0!important;min-width:0!important}
 body:not(.rima-live-landscape) #su>#train-step-1,
 body:not(.rima-live-landscape) #su>#train-step-2{grid-column:2!important;min-width:0!important;max-width:100%!important}
 body:not(.rima-live-landscape) #su>#train-step-1{grid-row:1!important}
 body:not(.rima-live-landscape) #su>#train-step-2{grid-row:1!important}
 body:not(.rima-live-landscape) #md{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:7px!important}
 body:not(.rima-live-landscape) #md .mc{min-height:58px!important;padding:10px 12px!important}
 body:not(.rima-live-landscape) #train-step-1 .stp{margin:5px 2px 8px!important}
 body:not(.rima-live-landscape) #train-step-1 .go{margin-top:9px!important}
 /* Keep the same three navigation destinations available in landscape. */
 nav{
  display:grid!important;visibility:visible!important;pointer-events:auto!important;
  position:fixed!important;left:12px!important;right:12px!important;bottom:calc(6px + env(safe-area-inset-bottom,0px))!important;
  width:auto!important;min-height:48px!important;height:auto!important;z-index:15000!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:6px!important;
  padding:4px 6px!important;border-radius:14px!important;
 }
 nav button{
  display:flex!important;flex-direction:row!important;align-items:center!important;justify-content:center!important;
  gap:7px!important;min-width:0!important;min-height:42px!important;height:42px!important;
  padding:4px 6px!important;font-size:clamp(10px,1.15vw,12px)!important;letter-spacing:.04em!important;
  white-space:nowrap!important;touch-action:manipulation!important;pointer-events:auto!important;
 }
 nav button svg{width:17px!important;height:17px!important;flex:0 0 17px!important}
 /* V51 owns player visibility: do not force #pbar on in landscape setup. */
 body:not(.rima-v51-player-eligible) #pbar{display:none!important;visibility:hidden!important;pointer-events:none!important}
 body.rima-v51-player-eligible #pbar{z-index:12000!important}
}
@media (orientation:landscape) and (max-width:559px){
 nav{display:grid!important;visibility:visible!important;pointer-events:auto!important;z-index:15000!important}
 body:not(.rima-live-landscape) main{position:relative!important;height:auto!important;max-height:none!important;overflow:visible!important;padding-bottom:76px!important}
}
</style>
<script id="rimalab-landscape-navigation-touch-runtime-v52">
(function(){
 'use strict';
 const nav=document.querySelector('body>nav'),main=document.querySelector('main');
 function landscape(){return !!(window.matchMedia&&window.matchMedia('(orientation:landscape)').matches)||innerWidth>innerHeight}
 function sync(){
  if(!landscape())return;
  const live=document.body.classList.contains('rima-live-landscape');
  if(nav&&!live){nav.style.setProperty('display','grid','important');nav.style.setProperty('visibility','visible','important');nav.style.setProperty('pointer-events','auto','important')}
  if(main&&!live){
   /* V49/V51 can reapply fixed/hidden inline geometry on stage changes. */
   for(const [k,v] of [['position','relative'],['inset','auto'],['left','auto'],['right','auto'],['top','auto'],['bottom','auto'],['height','auto'],['max-height','none'],['overflow-x','hidden'],['overflow-y','visible'],['touch-action','pan-y']])main.style.setProperty(k,v,'important');
   document.documentElement.style.setProperty('overflow-y','auto','important');
   document.body.style.setProperty('overflow-y','auto','important');
  }
 }
 function settle(){requestAnimationFrame(sync);setTimeout(sync,100);setTimeout(sync,300);setTimeout(sync,700)}
 const observer=new MutationObserver(()=>sync());
 observer.observe(document.body,{attributes:true,attributeFilter:['class']});
 window.addEventListener('orientationchange',settle,{passive:true});
 window.addEventListener('resize',settle,{passive:true});
 window.addEventListener('pageshow',settle,{passive:true});
 settle();window.rimaV52SyncLandscape=sync;
})();
</script>
'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V52_FAIL: </body> missing')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='72': raise SystemExit('V52_FAIL: expected base code 72')
g=g[:m.start()]+re.sub('72','73',m.group(0),count=1)+g[m.end():]
m=re.search(r"versionName\s*=\s*['\"]([^'\"]+)['\"]|versionName\s+['\"]([^'\"]+)['\"]",g)
if not m or (m.group(1) or m.group(2))!='3.3.0': raise SystemExit('V52_FAIL: expected base version 3.3.0')
g=g[:m.start()]+m.group(0).replace('3.3.0','3.3.1')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V52_OK: landscape nav restored; setup main scroll/touch restored; home selector adapts to landscape; player remains gated; version 3.3.1/code73')
