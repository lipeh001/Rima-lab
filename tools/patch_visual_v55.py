#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V55_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if 'rimalab-final-ui-fixes-v55' in h: raise SystemExit('V55_FAIL: patch já aplicado')
if 'rimalab-unified-catalog-favorites-v54' not in h: raise SystemExit('V55_FAIL: V54 ausente')
# Keep the live player subtitle tied to the actual selected/playing track, not the category tab.
runtime=r"""
<script id="rimalab-player-track-category-v55">
(function(){
 'use strict';
 function activeCategory(){
  try{
   if(typeof ZS==='undefined'||!ZS||ZS.k!=='lib'||!ZS.key)return 'App';
   const key=String(ZS.key);
   if(typeof ZLIB==='undefined'||!ZLIB)return 'App';
   for(const category of Object.keys(ZLIB)){
    const rows=ZLIB[category]&&ZLIB[category][1];
    if(Array.isArray(rows)&&rows.some(row=>typeof zKey==='function'&&String(zKey(row))===key))return category;
   }
  }catch(_){}
  return 'App';
 }
 function syncSubtitle(){
  const el=document.getElementById('pws');if(!el)return;
  const category=activeCategory();
  if(el.textContent!==category)el.textContent=category;
 }
 const oldBar=window.zBarUI;
 if(typeof oldBar==='function'&&!oldBar.__rimaV55){
  const wrapped=function(){const out=oldBar.apply(this,arguments);syncSubtitle();return out};
  wrapped.__rimaV55=true;window.zBarUI=wrapped;
 }
 const oldUI=window.zUI;
 if(typeof oldUI==='function'&&!oldUI.__rimaV55){
  const wrapped=function(){const out=oldUI.apply(this,arguments);syncSubtitle();return out};
  wrapped.__rimaV55=true;window.zUI=wrapped;
 }
 document.addEventListener('click',()=>requestAnimationFrame(syncSubtitle),true);
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)syncSubtitle()});
 window.addEventListener('focus',syncSubtitle);
 syncSubtitle();
})();
</script>
"""
h=h.replace('</body>',runtime+'\n</body>',1)
css=r"""
<style id="rimalab-final-ui-fixes-v55">
/* Stage 2 selector: do not crop the step heading or its contents. */
#train-step-2{box-sizing:border-box!important;min-width:0!important;max-width:100%!important;overflow:visible!important;padding-bottom:16px!important}
#train-step-2>.row:first-child{min-width:0!important;flex-wrap:wrap!important;gap:8px!important}
#train-step-2>.row:first-child .tag{flex:0 0 auto!important;white-space:nowrap!important;max-width:100%!important}
#train-step-2 .stp{min-width:0!important;max-width:100%!important;overflow:visible!important}
#train-step-2 #bp{min-width:0!important;max-width:100%!important;overflow:visible!important}
/* Same favorite-heart color/state in the setup, live selector and battle selector. */
#bp [data-rima-fav],#bq [data-rima-fav],#bbq [data-rima-fav],
#bp [data-v43-heart],#bq [data-v43-heart],#bbq [data-v43-heart],
#pbar #rima-v29-player-heart{color:#bdb6a6!important;border-color:rgba(255,203,84,.42)!important}
#bp [data-rima-fav].on,#bq [data-rima-fav].on,#bbq [data-rima-fav].on,
#bp [data-v43-heart].on,#bq [data-v43-heart].on,#bbq [data-v43-heart].on,
#pbar #rima-v29-player-heart.on{color:#ffcb54!important;background:rgba(255,203,84,.16)!important;border-color:#ffcb54!important}
/* Keep a little breathing room between the start message and the rhyme-tip control. */
#lv:not([hidden]) #stg.stage #ck{margin-bottom:14px!important}
#lv:not([hidden]) #stg.stage .v3bar{margin-top:12px!important;padding-top:4px!important}
/* The live landscape stage owns the screen; navigation must not cover the stage. */
@media(orientation:landscape) and (min-width:560px){
 body.rima-live-landscape nav{display:none!important;visibility:hidden!important;pointer-events:none!important}
 body.rima-live-landscape #lv:not([hidden]){padding-bottom:0!important;grid-template-rows:minmax(0,1fr)!important}
 body.rima-live-landscape #lv:not([hidden]) #stg.stage{min-height:0!important;height:100%!important;max-height:none!important;overflow:visible!important;box-sizing:border-box!important}
 body.rima-live-landscape #lv:not([hidden])>.card:not(.stage){min-height:0!important;max-height:none!important}
 body.rima-live-landscape #lv:not([hidden]) #bq{min-height:0!important;max-height:100%!important}
 body.rima-live-landscape #lv:not([hidden]) #bq>.bsl,
 body.rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist{min-height:0!important;max-height:100%!important}
}
/* Keep selector lists from clipping their own section on compact portrait screens. */
@media(orientation:portrait) and (max-width:760px){
 #train-step-2 #bp>.bsl,#train-step-2 #bp>.rima-v43-favlist{max-height:min(40vh,340px)!important}
}
</style>
"""
h=h.replace('</body>',css+'\n</body>',1)
# V54 produces version 3.3.3/code 75; increment patch version for this build.
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='75': raise SystemExit('V55_FAIL: versionCode base inesperado')
g=g[:m.start()]+re.sub('75','76',m.group(0),count=1)+g[m.end():]
m=re.search(r'versionName\s*=\s*[\'"]([^\'"]+)[\'"]|versionName\s+[\'"]([^\'"]+)[\'"]',g)
if not m or (m.group(1) or m.group(2))!='3.3.3': raise SystemExit('V55_FAIL: versionName base inesperado')
g=g[:m.start()]+m.group(0).replace('3.3.3','3.3.4')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V55_OK: player category bound to active track; favorite heart colors unified; step 2 clipping, landscape nav/stage and rhyme-tip spacing adjusted; version 3.3.4/code76')
