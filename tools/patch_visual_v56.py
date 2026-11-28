#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1]).resolve()
hp = root / "app/src/main/assets/rima-lab.html"
gp = next((p for p in (root/"app/build.gradle", root/"app/build.gradle.kts") if p.exists()), None)
if not hp.is_file() or gp is None:
    raise SystemExit("V56_FAIL: HTML/Gradle ausente")
h, g = hp.read_text(encoding="utf-8"), gp.read_text(encoding="utf-8")
if "rimalab-layout-and-heart-system-v56" in h:
    raise SystemExit("V56_FAIL: patch já aplicado")
if "rimalab-unified-catalog-favorites-v54" not in h:
    raise SystemExit("V56_FAIL: base V54/3.3.3 ausente")

# Keep the stored track identity/metadata unchanged; normalize only the displayed Favorites title.
sid = "rimalab-favorites-layout-runtime-v43"
m = re.search(r'<script\b[^>]*\bid=["\']'+sid+r'["\'][^>]*>(.*?)</script>', h, re.S)
if not m:
    raise SystemExit("V56_FAIL: runtime Favorites V43 ausente")
js = m.group(1)
old = "const title=esc(t.x[1]),artist=esc(t.x[6]||'Artista independente'),key=esc(t.key);"
new = "const title=esc(String(t.x[1]||'').normalize('NFC').replace(/\\s+/gu,' ').trim()),artist=esc(t.x[6]||'Artista independente'),key=esc(t.key);"
if js.count(old) != 1:
    raise SystemExit("V56_FAIL: renderização de título não corresponde à base 3.3.3")
h = h[:m.start(1)] + js.replace(old, new, 1) + h[m.end(1):]

css = r'''<style id="rimalab-layout-and-heart-system-v56">
/* Step 2: restore a safe inner gutter without changing the catalog or its click targets. */
#train-step-2 #bp{box-sizing:border-box!important;display:block!important;position:relative!important;width:100%!important;max-width:100%!important;min-width:0!important;padding:0 6px!important;overflow-x:visible!important}
#train-step-2 #bp>.bsl,#train-step-2 #bp>.rima-v43-favlist{box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;padding:6px 9px 8px!important;margin:7px 0 8px!important;overflow-x:hidden!important}
#train-step-2 #bp .bi,#train-step-2 #bp .rima-v43-fav-row{box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;margin-left:0!important;margin-right:0!important}
#train-step-2 #bp .beat-info{box-sizing:border-box!important;min-width:0!important;max-width:100%!important;flex:1 1 0%!important}
#train-step-2 #bp .mc{box-sizing:border-box!important;min-width:0!important;max-width:100%!important;white-space:normal!important;overflow-wrap:anywhere!important}

/* Favorites: compact, readable titles; remove repeated spacing from imported titles. */
#bp .rima-v43-fav-play,#bq .rima-v43-fav-play,#bbq .rima-v43-fav-play{text-align:left!important;letter-spacing:normal!important;word-spacing:normal!important;line-height:1.12!important;white-space:normal!important;overflow-wrap:anywhere!important}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;max-width:100%!important;margin:0!important;overflow:hidden!important;text-align:left!important;letter-spacing:normal!important;word-spacing:normal!important;line-height:1.12!important}
#bp .rima-v43-fav-row,#bq .rima-v43-fav-row,#bbq .rima-v43-fav-row{min-width:0!important;gap:8px!important;padding:4px 0!important}
#bp .rima-v43-fav-row>.beat-info,#bq .rima-v43-fav-row>.beat-info,#bbq .rima-v43-fav-row>.beat-info{flex:1 1 0%!important;min-width:0!important}

/* All favorite-heart buttons share one square, centered vector glyph. */
.rima-heart-host{display:inline-flex!important;align-items:center!important;justify-content:center!important;gap:6px!important;line-height:1!important;text-align:center!important;-webkit-text-stroke:0!important;text-shadow:none!important}
.rima-heart-icon{display:block!important;flex:0 0 20px!important;width:20px!important;height:20px!important;min-width:20px!important;min-height:20px!important;max-width:20px!important;max-height:20px!important;aspect-ratio:1/1!important;overflow:visible!important;transform:none!important;pointer-events:none!important}
.rima-heart-icon path{stroke:currentColor!important;stroke-width:1.8!important;stroke-linecap:round!important;stroke-linejoin:round!important;fill:none!important}
.rima-heart-icon[data-filled="true"] path{fill:currentColor!important;stroke:currentColor!important;stroke-width:1.1!important}
#bp .rima-v43-fav-heart,#bq .rima-v43-fav-heart,#bbq .rima-v43-fav-heart,#bp .rima-v29-fav,#bq .rima-v29-fav,#bbq .rima-v29-fav,#bp [data-rima-fav],#bq [data-rima-fav],#bbq [data-rima-fav],#pbar #rima-v29-player-heart{box-sizing:border-box!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;padding:0!important;aspect-ratio:1/1!important;line-height:1!important}
#bp .rima-v43-tools button,#bq .rima-v43-tools button,#bbq .rima-v43-tools button{display:flex!important;align-items:center!important;justify-content:center!important;gap:7px!important}

/* Vertical live selector: reserve a usable scrolling viewport, like setup step 2. */
@media(orientation:portrait) and (max-width:760px){
 html body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage){display:flex!important;flex:0 0 auto!important;flex-direction:column!important;box-sizing:border-box!important;width:100%!important;min-width:0!important;min-height:0!important;height:auto!important;max-height:none!important;overflow:visible!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq{display:flex!important;flex:0 0 auto!important;flex-direction:column!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;min-height:0!important;height:auto!important;max-height:none!important;overflow:visible!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq>.bsl:not([hidden]),html body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden]){display:block!important;flex:0 0 auto!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;height:auto!important;min-height:min(20vh,175px)!important;max-height:min(26vh,220px)!important;margin:3px 0 5px!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important}
 html body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage)>.row.nw{flex:0 0 auto!important;min-height:0!important;margin:0 0 2px!important;gap:5px!important;font-size:15px!important;line-height:1.15!important}
 html body.pl:not(.pv) #lv:not([hidden])>.card:not(.stage)>p.mut{flex:0 0 auto!important;margin:1px 0 2px!important;font-size:12px!important;line-height:1.15!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq>p.mut:first-child{display:none!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v50-category-row{flex:0 0 36px!important;height:36px!important;min-height:36px!important;margin:3px 0 4px!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-tools{flex:0 0 38px!important;height:38px!important;min-height:38px!important;margin:2px 0 4px!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq>.rima-v43-tools button{height:38px!important;min-height:38px!important;padding:5px 10px!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq>p.mut:not(:first-child){display:block!important;flex:0 0 14px!important;height:14px!important;min-height:14px!important;max-height:14px!important;margin:1px 0!important;padding:0!important;overflow:hidden!important;white-space:nowrap!important;text-overflow:ellipsis!important;font-size:9px!important;line-height:14px!important}
 html body.pl:not(.pv) #lv:not([hidden]) #bq>.catalog-attribution,html body.pl:not(.pv) #lv:not([hidden]) #bq>.bsw{display:none!important}
 html body.pl:not(.pv) #lv:not([hidden]) #stg.stage #cn:not(:empty){position:relative!important;transform:none!important;margin:8px auto 9px!important;line-height:1.3!important}
 html body.pl:not(.pv) #lv:not([hidden]) #stg.stage .v3bar{position:relative!important;inset:auto!important;display:flex!important;flex:0 0 auto!important;width:100%!important;min-width:0!important;max-width:100%!important;min-height:44px!important;height:auto!important;align-items:center!important;justify-content:center!important;margin:8px auto 5px!important;padding:3px 5px 4px!important;box-sizing:border-box!important}
 html body.pl:not(.pv) #lv:not([hidden]) #stg.stage .v3bar button{box-sizing:border-box!important;max-width:100%!important;min-width:0!important;min-height:36px!important;height:auto!important;padding:6px 10px!important;white-space:normal!important;overflow-wrap:anywhere!important;line-height:1.2!important}
}

/* Landscape: compact category controls above a dedicated scrollable beat-list row. */
@media(orientation:landscape) and (min-width:560px){
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]){grid-template-rows:36px minmax(0,1fr) 34px!important;gap:5px 10px!important;padding:6px max(12px,env(safe-area-inset-right,0px)) calc(var(--rima-stage-bottom,108px) + 3px) max(12px,env(safe-area-inset-left,0px))!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.bk{height:36px!important;min-height:36px!important;margin:0!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.btn.w{height:34px!important;min-height:34px!important;margin:0!important;padding:4px 8px!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage){display:flex!important;flex-direction:column!important;box-sizing:border-box!important;width:100%!important;height:100%!important;max-height:100%!important;min-height:0!important;padding:7px 9px!important;overflow:hidden!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage)>.row.nw{flex:0 0 auto!important;min-height:0!important;margin:0 0 2px!important;gap:5px!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage)>p.mut{flex:0 0 auto!important;margin:1px 0 2px!important;font-size:11px!important;line-height:1.15!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>.card:not(.stage)>div:not(.row){display:flex!important;flex:1 1 0%!important;flex-direction:column!important;min-height:0!important;height:auto!important;max-height:none!important;overflow:hidden!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq{display:grid!important;position:relative!important;flex:1 1 0%!important;grid-template-columns:minmax(0,1fr) 88px!important;grid-template-rows:30px 12px minmax(0,1fr)!important;column-gap:7px!important;row-gap:3px!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;min-width:0!important;height:100%!important;max-height:100%!important;min-height:0!important;overflow:hidden!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>p.mut:first-child{display:none!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row,html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.row{grid-column:1!important;grid-row:1!important;display:flex!important;flex:0 0 30px!important;width:100%!important;min-width:0!important;min-height:30px!important;height:30px!important;align-items:center!important;gap:4px!important;margin:0!important;padding:0!important;overflow:hidden!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v50-category-row>.tag.chip{display:flex!important;flex:1 1 0%!important;min-width:0!important;max-width:none!important;align-items:center!important;justify-content:center!important;box-sizing:border-box!important;padding:4px 1px!important;margin:0!important;font-size:clamp(8px,.95vw,11px)!important;line-height:1.05!important;white-space:nowrap!important;overflow:hidden!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools{grid-column:2!important;grid-row:1!important;display:flex!important;flex:0 0 30px!important;width:100%!important;max-width:100%!important;min-width:0!important;height:30px!important;min-height:30px!important;margin:0!important;padding:0!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-tools button{width:100%!important;min-width:0!important;max-width:100%!important;height:30px!important;min-height:30px!important;padding:2px!important;font-size:10px!important;gap:3px!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>p.mut:not(:first-child){grid-column:1 / -1!important;grid-row:2!important;display:block!important;flex:0 0 12px!important;height:12px!important;min-height:12px!important;max-height:12px!important;margin:0!important;padding:0!important;overflow:hidden!important;white-space:nowrap!important;text-overflow:ellipsis!important;font-size:8px!important;line-height:12px!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsl:not([hidden]),html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.rima-v43-favlist:not([hidden]){grid-column:1 / -1!important;grid-row:3!important;display:block!important;position:relative!important;flex:1 1 0%!important;box-sizing:border-box!important;width:100%!important;min-width:0!important;min-height:64px!important;height:auto!important;max-height:none!important;margin:0!important;padding:3px 5px!important;overflow-y:auto!important;overflow-x:hidden!important;overscroll-behavior:contain!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.catalog-attribution,html body.pl:not(.pv).rima-live-landscape #lv:not([hidden]) #bq>.bsw{display:none!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage{display:flex!important;position:relative!important;flex-direction:column!important;justify-content:flex-start!important;align-items:stretch!important;box-sizing:border-box!important;min-width:0!important;min-height:0!important;width:100%!important;height:100%!important;max-height:100%!important;overflow:hidden!important;padding:10px 12px 12px!important;gap:0!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage #ck{flex:0 0 auto!important;margin:0 0 5px!important;line-height:1.15!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage #cb{flex:1 1 auto!important;display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;min-width:0!important;min-height:38px!important;height:auto!important;max-height:none!important;margin:0 auto!important;padding:3px 4px!important;box-sizing:border-box!important;line-height:1.02!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage #cs:not(:empty){flex:0 1 auto!important;margin:5px auto 6px!important;line-height:1.15!important;max-width:100%!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage #rm{flex:0 1 auto!important;gap:3px!important;margin:3px auto!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage #sg{flex:0 0 auto!important;min-height:4px!important;margin:3px 0!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage #cn:not(:empty){flex:0 0 auto!important;transform:none!important;margin:5px auto 8px!important;line-height:1.15!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage .v3bar{position:relative!important;inset:auto!important;z-index:7!important;display:flex!important;flex:0 0 auto!important;width:100%!important;min-width:0!important;min-height:38px!important;height:auto!important;max-height:none!important;align-items:center!important;justify-content:center!important;margin:auto auto 1px!important;padding:3px 0 4px!important;box-sizing:border-box!important}
 html body.pl:not(.pv).rima-live-landscape #lv:not([hidden])>#stg.stage .v3bar button{max-width:100%!important;min-width:0!important;min-height:34px!important;height:auto!important;padding:5px 10px!important;white-space:normal!important;line-height:1.15!important}
}
</style>'''
runtime = r'''<script id="rimalab-centered-heart-runtime-v56">
(function(){
 'use strict';
 const NS='http://www.w3.org/2000/svg',PATH='M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78Z';
 const selector='button.rima-v43-fav-heart,button.rima-v29-fav,button[data-rima-fav],button[data-v43-heart],button#rima-v29-player-heart,button.rima-v43-toggle,button.rima-v42-favorites-toggle,button.rima-v29-tools button,button#rima-v29-favs';
 function apply(b){
  if(!b||b.tagName!=='BUTTON')return;
  const matches=b.matches(selector),nodes=[];let solid=false;
  const w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT);let n,seen=false;
  while((n=w.nextNode()))if(/[\u2665\u2661]/.test(n.nodeValue||'')){seen=true;if(/\u2665/.test(n.nodeValue))solid=true;nodes.push(n)}
  if(!matches&&!seen)return;
  const existing=b.querySelector(':scope > svg.rima-heart-icon');
  if(existing){nodes.forEach(x=>x.nodeValue=x.nodeValue.replace(/[\u2665\u2661]/g,''));return}
  if(!seen)return;
  nodes.forEach(x=>x.nodeValue=x.nodeValue.replace(/[\u2665\u2661]/g,''));
  const filled=solid||b.classList.contains('on')||b.getAttribute('aria-pressed')==='true';
  const svg=document.createElementNS(NS,'svg');svg.setAttribute('class','rima-heart-icon');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('width','20');svg.setAttribute('height','20');svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');svg.setAttribute('data-filled',filled?'true':'false');
  const p=document.createElementNS(NS,'path');p.setAttribute('d',PATH);svg.appendChild(p);b.classList.add('rima-heart-host');b.insertBefore(svg,b.firstChild);
 }
 function scan(root){const scope=root&&root.querySelectorAll?root:document;if(root&&root.matches&&root.matches('button'))apply(root);scope.querySelectorAll('button').forEach(apply)}
 scan(document);
 if(document.body&&window.MutationObserver){new MutationObserver(records=>records.forEach(r=>r.addedNodes.forEach(n=>{if(n.nodeType===1)scan(n);else if(n.nodeType===3&&n.parentElement)apply(n.parentElement.closest('button'))}))).observe(document.body,{subtree:true,childList:true})}
 window.rimaV56RefreshHearts=()=>scan(document);
})();
</script>'''
pos = h.lower().rfind("</body>")
if pos < 0:
    raise SystemExit("V56_FAIL: </body> ausente")
h = h[:pos] + css + "\n" + runtime + "\n" + h[pos:]

vm = re.search(r'\bversionCode\s*=\s*(\d+)|\bversionCode\s+(\d+)', g)
if not vm or (vm.group(1) or vm.group(2)) != "75":
    raise SystemExit("V56_FAIL: versionCode base não é 75")
g = g[:vm.start()] + re.sub("75", "76", vm.group(0), count=1) + g[vm.end():]
nm = re.search(r'versionName\s*=\s*["\']([^"\']+)["\']|versionName\s+["\']([^"\']+)["\']', g)
if not nm or (nm.group(1) or nm.group(2)) != "3.3.3":
    raise SystemExit("V56_FAIL: versionName base não é 3.3.3")
g = g[:nm.start()] + nm.group(0).replace("3.3.3", "3.3.4") + g[nm.end():]
hp.write_text(h, encoding="utf-8")
gp.write_text(g, encoding="utf-8")
print("V56_OK: 3.3.3 base preserved; step2 inset, compact Favorites titles, square SVG hearts, vertical selector height, landscape list and contained tip; 3.3.4/code76")
