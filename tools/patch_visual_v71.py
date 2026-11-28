#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V71_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-root-layout-player-v71' in h: raise SystemExit('V71_FAIL: patch já aplicado')
# Normalize titles at the data/state boundary, so list, player and stage use
# the exact same canonical title (including NBSP/zero-width/repeated spaces).
old="ZS.name=x[1];ZS.bpm=ZS.b0=x[2]||ZLIB[ZS.s][0];"
new="ZS.name=(typeof rimaV59CleanTitle==='function'?rimaV59CleanTitle(x[1]):String(x[1]||'').replace(/[\\s\\u00A0]+/gu,' ').trim());ZS.bpm=ZS.b0=x[2]||ZLIB[ZS.s][0];"
if h.count(old)!=1: raise SystemExit('V71_FAIL: atribuição do nome da faixa não encontrada')
h=h.replace(old,new,1)
# Ensure the player subtitle communicates loading instead of showing genre
# while audio is still opening.
old="s.textContent=ZS.k=='lib'?ZS.s:'App';b.innerHTML=zPL?ZPAU:ZPLAY;"
new="s.textContent=ZS.loadingAudio?'Abrindo o beat...':(ZS.k=='lib'?ZS.s:'App');b.innerHTML=zPL?ZPAU:ZPLAY;"
if h.count(old)!=1: raise SystemExit('V71_FAIL: zBarUI subtitle not found uniquely')
h=h.replace(old,new,1)
# The old beat pulse scaled the frame beyond the clipped stage, hiding side
# borders and making the entire stage appear to resize on each word change.
old="const scale=p<.34?1+.035*(p/.34):1+.035*(1-(p-.34)/.66);"
new="const scale=1;"
if h.count(old)!=1: raise SystemExit('V71_FAIL: pulse scale formula not found uniquely')
h=h.replace(old,new,1)
css=r'''<style id="rimalab-root-layout-player-v71">
/* Fixed stage geometry: word length and the pulse may change glow, never layout. */
#lv:not([hidden]) #stg.stage{
 box-sizing:border-box!important;position:relative!important;
 width:100%!important;height:450px!important;min-height:450px!important;
 max-height:450px!important;flex:0 0 450px!important;
 border:1.6px solid rgba(237,195,77,.58)!important;
 border-radius:22px!important;overflow:hidden!important;
 transform:none!important;transition:none!important
}
#lv:not([hidden]) #stg.stage>.rima-beat-frame{
 position:absolute!important;inset:5px!important;display:block!important;
 width:auto!important;height:auto!important;box-sizing:border-box!important;
 border:1.5px solid rgba(237,195,77,.42)!important;
 border-radius:17px!important;transform:scale(1)!important;
 transform-origin:center!important;pointer-events:none!important
}
/* A fixed word lane prevents long/short words from changing the stage height. */
#lv:not([hidden]) #stg.stage #cb{
 box-sizing:border-box!important;display:flex!important;
 flex:0 0 150px!important;height:150px!important;min-height:150px!important;
 max-height:150px!important;width:100%!important;max-width:100%!important;
 align-items:center!important;justify-content:center!important;
 overflow:hidden!important;white-space:normal!important;
 contain:layout paint!important
}
#lv:not([hidden]) #stg.stage #ck{flex:0 0 auto!important;min-height:22px!important}
#lv:not([hidden]) #stg.stage #cs{
 flex:0 0 auto!important;min-height:42px!important;max-height:42px!important;
 display:flex!important;align-items:center!important;justify-content:center!important;
 overflow:hidden!important
}
#lv:not([hidden]) #stg.stage #sg{flex:0 0 8px!important;height:8px!important;min-height:8px!important}
#lv:not([hidden]) #stg.stage #cn{flex:0 0 22px!important;min-height:22px!important;max-height:22px!important}
#lv:not([hidden]) #stg.stage .v3bar{flex:0 0 42px!important;min-height:42px!important;max-height:42px!important}
/* Player title: measure intrinsic text width after font loading, then loop with a real gap. */
#pbar .pwi{flex:1 1 0!important;min-width:0!important;max-width:none!important;overflow:hidden!important}
#pbar #pwn{display:block!important;width:100%!important;min-width:0!important;
 max-width:none!important;overflow:hidden!important;white-space:nowrap!important;
 text-overflow:clip!important}
#pbar #pwn .rima-title-track{display:inline-flex!important;width:max-content!important;
 max-width:none!important;white-space:nowrap!important;align-items:center!important;
 flex-wrap:nowrap!important;will-change:transform!important}
#pbar #pwn .rima-title-track>span{display:inline-block!important;width:max-content!important;
 max-width:none!important;flex:0 0 auto!important;white-space:nowrap!important}
#pbar #pwn .rima-title-track>i{display:block!important;width:76px!important;
 min-width:76px!important;flex:0 0 76px!important;height:1px!important}
#pbar #pwn .rima-title-track.is-long{animation:rima-title-marquee-v69 linear infinite!important}
#pbar #pwn .rima-title-track:not(.is-long){animation:none!important}
@media(prefers-reduced-motion:reduce){#pbar #pwn .rima-title-track.is-long{animation:none!important}}
/* Keep local-save metadata wrapping identical in category lists and Favorites. */
#bp .beat-meta,#bq .beat-meta,#bbq .beat-meta{
 display:flex!important;align-items:baseline!important;flex-wrap:wrap!important;
 gap:4px 8px!important;min-width:0!important;white-space:normal!important
}
#bp .beat-meta .okc,#bq .beat-meta .okc,#bbq .beat-meta .okc,
#bp .rima-v43-fav-row .okc,#bq .rima-v43-fav-row .okc,#bbq .rima-v43-fav-row .okc{
 display:inline!important;flex:0 1 auto!important;white-space:normal!important;
 overflow-wrap:normal!important;word-break:normal!important;
 font:600 13px/1.3 'Archivo',system-ui,sans-serif!important
}
</style>
<script id="rimalab-player-marquee-measure-v71">
(function(){
 const measure=()=>{
  const e=document.getElementById('pwn'),track=e&&e.querySelector('.rima-title-track');
  if(!e||!track||!track.firstElementChild)return;
  const first=track.firstElementChild;
  const natural=Math.max(first.scrollWidth,first.getBoundingClientRect().width);
  const available=e.clientWidth;
  const long=natural>available+4;
  track.classList.toggle('is-long',long);
  if(long)track.style.animationDuration=Math.max(9,Math.min(28,(natural+76)/34))+'s';
  else track.style.animationDuration='0s';
 };
 const schedule=()=>{requestAnimationFrame(()=>requestAnimationFrame(measure))};
 if(document.fonts&&document.fonts.ready)document.fonts.ready.then(schedule).catch(()=>{});
 window.addEventListener('resize',schedule,{passive:true});
 const bar=document.getElementById('pbar');
 if(bar&&typeof MutationObserver!=='undefined'){
  new MutationObserver(schedule).observe(bar,{subtree:true,childList:true,characterData:true});
 }
 schedule();
 window.rimaPlayerMarqueeMeasureV71=measure;
})();
</script>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V71_FAIL: body ausente')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='90': raise SystemExit('V71_FAIL: versionCode base não é 90')
g=g[:m.start(1)]+'91'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.8': raise SystemExit('V71_FAIL: versionName base não é 3.4.8')
g=g[:m.start(1)]+'3.4.9'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V71_OK: no-scale stage pulse; fixed stage and word lane; canonical title state; measured marquee; loading subtitle; unified local-save wrapping; 3.4.9/code91')
