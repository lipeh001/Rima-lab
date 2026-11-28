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

# V56: fix remaining selector geometry, Favorites spacing and heart artwork.
if 'rimalab-layout-and-heart-system-v56' in h:
    raise SystemExit('V56_FAIL: patch já aplicado')

runtime = r"""
<script id="rimalab-heart-svg-runtime-v56">
(function(){
 const NS='http://www.w3.org/2000/svg';
 const D='M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78Z';
 let queued=false;
 function apply(b){
  if(!b||b.tagName!=='BUTTON')return;
  const known=b.matches('.rima-v43-fav-heart,.rima-v29-fav,#rima-v29-player-heart,[data-rima-fav],[data-v43-heart],.rima-v43-toggle,.rima-v42-favorites-toggle');
  if(!known&&!/[♡♥]/u.test(b.textContent||''))return;
  let svg=b.querySelector(':scope > svg.rima-heart-svg');
  const walker=document.createTreeWalker(b,NodeFilter.SHOW_TEXT);let n;
  while((n=walker.nextNode()))if(/[♡♥]/u.test(n.nodeValue||''))n.nodeValue=n.nodeValue.replace(/[♡♥]/gu,'');
  if(!svg){
   svg=document.createElementNS(NS,'svg');
   svg.setAttribute('class','rima-heart-svg');
   svg.setAttribute('viewBox','0 0 24 24');
   svg.setAttribute('aria-hidden','true');
   svg.setAttribute('focusable','false');
   const p=document.createElementNS(NS,'path');p.setAttribute('d',D);svg.appendChild(p);b.insertBefore(svg,b.firstChild);
  }
  const label=(b.getAttribute('aria-label')||'').toLowerCase();
  const filled=b.classList.contains('on')||b.classList.contains('active')||label.includes('remover dos favoritos')||(b.textContent||'').toLowerCase().includes('favoritos');
  svg.setAttribute('data-filled',filled?'true':'false');b.classList.add('rima-heart-svg-button');
 }
 function refresh(){queued=false;document.querySelectorAll('button').forEach(apply)}
 function schedule(){if(!queued){queued=true;requestAnimationFrame(refresh)}}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',schedule,{once:true});else schedule();
 if(document.body&&window.MutationObserver)new MutationObserver(schedule).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','aria-label']});
 window.rimaV56RefreshHearts=refresh;
})();
</script>
"""
css = r"""
<style id="rimalab-layout-and-heart-system-v56">
.rima-heart-svg-button{display:inline-flex!important;align-items:center!important;justify-content:center!important;gap:7px!important;line-height:1!important;-webkit-text-stroke:0!important;text-shadow:none!important}
.rima-heart-svg{display:block!important;flex:0 0 19px!important;width:19px!important;height:19px!important;min-width:19px!important;min-height:19px!important;max-width:19px!important;max-height:19px!important;aspect-ratio:1/1!important;transform:none!important}
.rima-heart-svg path{fill:currentColor;stroke:currentColor;stroke-width:1.05;stroke-linecap:round;stroke-linejoin:round}
.rima-heart-svg[data-filled="false"] path{fill:none;stroke:currentColor;stroke-width:1.85}
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,#bp .rima-v29-fav,#bq .rima-v29-fav,#bbq .rima-v29-fav,#bp [data-rima-fav],#bq [data-rima-fav],#bbq [data-rima-fav],#pbar #rima-v29-player-heart{display:inline-flex!important;align-items:center!important;justify-content:center!important;box-sizing:border-box!important;padding:0!important;line-height:1!important;aspect-ratio:1/1!important;color:#c9bd98!important;border-color:rgba(255,203,84,.48)!important;-webkit-text-stroke:0!important;text-shadow:none!important}
#bp .rima-v43-fav-heart.on,#bq .rima-v43-fav-heart.on,#bbq .rima-v43-fav-heart.on,#bp .rima-v29-fav.on,#bq .rima-v29-fav.on,#bbq .rima-v29-fav.on,#bp [data-rima-fav].on,#bq [data-rima-fav].on,#bbq [data-rima-fav].on,#pbar #rima-v29-player-heart.on{color:#ffcf55!important;background:rgba(255,203,84,.16)!important;border-color:#ffcf55!important}
#bp .rima-v43-toggle,#bq .rima-v43-toggle,#bbq .rima-v43-toggle{display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important}
#train-step-2,#train-step-2 #bp{box-sizing:border-box!important;min-width:0!important;width:100%!important;max-width:100%!important}
#train-step-2 #bp{padding:0 3px!important;overflow-x:hidden!important;overflow-y:visible!important}
#train-step-2 #bp>.bsl,#train-step-2 #bp>.rima-v43-favlist{box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;padding:6px 7px 7px!important;margin:7px 0 8px!important;overflow-x:hidden!important}
#train-step-2 #bp .bi,#train-step-2 #bp .rima-v43-fav-row{box-sizing:border-box!important;min-width:0!important;width:100%!important;margin-left:0!important;margin-right:0!important}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row{gap:8px!important;padding:4px 0!important;align-items:center!important}
#bp .rima-v43-fav-row>.beat-info,#bq .rima-v43-fav-row>.beat-info,#bbq .rima-v43-fav-row>.beat-info{gap:2px!important;min-width:0!important}
#bp .rima-v43-favlist .rima-v43-fav-play,#bq .rima-v43-favlist .rima-v43-fav-play,#bbq .rima-v43-favlist .rima-v43-fav-play{min-height:0!important;height:auto!important;max-height:none!important;padding:7px 10px 6px!important;line-height:1.1!important;letter-spacing:normal!important;word-spacing:normal!important;white-space:normal!important}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;overflow:hidden!important;margin:0!important;line-height:1.1!important;letter-spacing:normal!important;word-spacing:normal!important}
#bp .rima-v43-fav-row .beat-meta,#bq .rima-v43-fav-row .beat-meta,#bbq .rima-v43-fav-row .beat-meta{min-height:0!important;padding:3px 10px 5px!important;line-height:1.15!important}
#bp .rima-v43-fav-row>.rima-v43-fav-heart,#bq .rima-v43-fav-row>.rima-v43-fav-heart,#bbq .rima-v43-fav-row>.rima-v43-fav-heart{display:inline-flex!important;place-items:center!important;flex:0 0 38px!important;width:38px!important;min-width:38px!important;height:38px!important;min-height:38px!important;padding:0!important;align-self:center!important}
@media(orientation:portrait) and (max-width:760px){
 body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage){display:flex!important;flex-direction:column!important;height:auto!important;min-height:0!important;max-height:none!important;overflow:visible!important;box-sizing:border-box!important}
 body.pl:not(.pv) #lv:not([hidden]) #bq{display:flex!important;flex:0 0 auto!important;flex-direction:column!important;width:100%!important;max-width:100%!important;min-width:0!important;min-height:0!important;overflow:visible!important}
 body.pl:not(.pv) #lv:not([hidden]) #bq>.bsl,body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-favlist{flex:0 0 auto!important;height:auto!important;min-height:min(24vh,185px)!important;max-height:min(40vh,340px)!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important}
 body.pl:not(.pv) #lv:not([hidden]) #stg.stage #cs:not(:empty){margin:14px auto 18px!important;line-height:1.35!important}
 body.pl:not(.pv) #lv:not([hidden]) #stg.stage #cn:not(:empty){transform:none!important;margin:8px auto 10px!important;line-height:1.25!important}
 body.pl:not(.pv) #lv:not([hidden]) #stg.stage .v3bar{margin:18px auto 5px!important;padding:5px 0 4px!important;min-height:42px!important}
 body.pl:not(.pv) #lv:not([hidden]) #stg.stage .v3bar button{max-width:100%!important;white-space:normal!important}
}
@media(orientation:landscape) and (min-width:560px){
 body.rima-live-landscape #lv:not([hidden]){display:grid!important;position:fixed!important;inset:0!important;width:100vw!important;max-width:100vw!important;height:100vh!important;min-height:0!important;max-height:100vh!important;box-sizing:border-box!important;grid-template-columns:minmax(0,1.18fr) minmax(0,.82fr)!important;grid-template-rows:42px minmax(0,1fr) 42px!important;gap:8px 12px!important;padding:8px max(12px,env(safe-area-inset-right,0px)) calc(var(--rima-stage-bottom,108px) + 4px) max(12px,env(safe-area-inset-left,0px))!important;overflow:hidden!important;align-items:stretch!important;align-content:stretch!important}
 body.rima-live-landscape #lv:not([hidden])>.bk{grid-column:2!important;grid-row:1!important;width:100%!important;height:42px!important;min-height:42px!important;margin:0!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage{grid-column:1!important;grid-row:1/4!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;align-items:stretch!important;box-sizing:border-box!important;width:100%!important;height:100%!important;min-width:0!important;min-height:0!important;max-height:none!important;margin:0!important;overflow:hidden!important;padding:clamp(9px,1.5vh,16px) clamp(10px,1.4vw,18px)!important;gap:0!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage #ck{flex:0 0 auto!important;margin:0 0 5px!important;line-height:1.15!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage #cb{flex:1 1 auto!important;display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;min-width:0!important;min-height:58px!important;height:auto!important;max-height:none!important;margin:0 auto!important;padding:3px 4px!important;box-sizing:border-box!important;line-height:1.02!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage #cs:not(:empty){flex:0 1 auto!important;margin:7px auto 8px!important;line-height:1.2!important;max-width:100%!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage #rm{flex:0 1 auto!important;gap:4px!important;margin:4px auto!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage #rm>*{max-width:24%!important;padding:3px 5px!important;font-size:clamp(9px,1.05vw,12px)!important;line-height:1.08!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage #sg{flex:0 0 auto!important;min-height:5px!important;margin:3px 0 2px!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage #cn:not(:empty){flex:0 0 auto!important;transform:none!important;margin:5px auto 6px!important;line-height:1.15!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage .v3bar{position:relative!important;inset:auto!important;z-index:7!important;display:flex!important;flex:0 0 auto!important;width:100%!important;min-width:0!important;min-height:36px!important;height:auto!important;align-items:center!important;justify-content:center!important;margin:9px auto 1px!important;padding:2px 0 3px!important}
 body.rima-live-landscape #lv:not([hidden])>#stg.stage .v3bar button{max-width:100%!important;min-width:0!important;min-height:34px!important;height:auto!important;padding:5px 10px!important;white-space:normal!important;line-height:1.15!important}
 body.rima-live-landscape #lv:not([hidden])>.card:not(.stage){grid-column:2!important;grid-row:2!important;display:flex!important;flex-direction:column!important;width:100%!important;height:100%!important;min-width:0!important;min-height:0!important;max-height:none!important;margin:0!important;padding:10px 12px!important;box-sizing:border-box!important;overflow:hidden!important}
 body.rima-live-landscape #lv:not([hidden])>.card:not(.stage)>.row.nw,body.rima-live-landscape #lv:not([hidden])>.card:not(.stage)>p.mut{flex:0 0 auto!important}
 body.rima-live-landscape #lv:not([hidden]) #bq{display:flex!important;flex:1 1 auto!important;flex-direction:column!important;width:100%!important;max-width:100%!important;min-width:0!important;min-height:0!important;overflow:hidden!important}
 body.rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools,body.rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-toggle,body.rima-live-landscape #lv:not([hidden]) #bq>.row,body.rima-live-landscape #lv:not([hidden]) #bq>.catalog-attribution{flex:0 0 auto!important;min-height:0!important}
 body.rima-live-landscape #lv:not([hidden]) #bq>.bsl,body.rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist{display:block!important;flex:1 1 0%!important;width:100%!important;min-width:0!important;min-height:78px!important;height:auto!important;max-height:none!important;margin:5px 0 3px!important;box-sizing:border-box!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important}
 body.rima-live-landscape #lv:not([hidden])>.btn.w{grid-column:2!important;grid-row:3!important;align-self:stretch!important;width:100%!important;height:42px!important;min-height:42px!important;margin:0!important;padding:5px 10px!important}
 body.rima-live-landscape nav{display:none!important;visibility:hidden!important;pointer-events:none!important}
}
</style>
"""
h=h.replace('</body>',runtime+'\n'+css+'\n</body>',1)
m=re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)',g)
if not m or (m.group(1) or m.group(2))!='76': raise SystemExit('V56_FAIL: versionCode base não é 76')
g=g[:m.start()]+re.sub('76','77',m.group(0),count=1)+g[m.end():]
m=re.search(r'versionName\s*=\s*[\'"]([^\'"]+)[\'"]|versionName\s+[\'"]([^\'"]+)[\'"]',g)
if not m or (m.group(1) or m.group(2))!='3.3.4': raise SystemExit('V56_FAIL: versionName base não é 3.3.4')
g=g[:m.start()]+m.group(0).replace('3.3.4','3.3.5')+g[m.end():]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V56_OK: step2 crop, compact Favorites titles, centered SVG hearts, portrait selector and landscape stage/list; version 3.3.5/code77')

