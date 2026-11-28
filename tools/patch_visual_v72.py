#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V72_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-stage-restart-pulse-marquee-v72' in h: raise SystemExit('V72_FAIL: patch já aplicado')
old='const scale=1;'
new='const scale=p<.34?1+.035*(p/.34):1+.035*(1-(p-.34)/.66);'
if h.count(old)!=1: raise SystemExit('V72_FAIL: escala de pulso não encontrada')
h=h.replace(old,new,1)
a=h.find('<style id="rimalab-root-layout-player-v71">');b=h.find('</style>',a)
if a<0 or b<0: raise SystemExit('V72_FAIL: bloco de layout V71 ausente')
h=h[:a]+'''<style id="rimalab-stage-restart-pulse-marquee-v72">
/* Responsive stage; word lane fixed so text changes never resize the frame. */
#lv:not([hidden]) #stg.stage{box-sizing:border-box!important;position:relative!important;overflow:hidden!important;transform:none!important;transition:none!important}
#lv:not([hidden]) #stg.stage #cb{box-sizing:border-box!important;display:flex!important;align-items:center!important;justify-content:center!important;width:100%!important;max-width:100%!important;min-height:clamp(88px,17vh,132px)!important;height:clamp(88px,17vh,132px)!important;max-height:clamp(88px,17vh,132px)!important;flex:0 0 clamp(88px,17vh,132px)!important;overflow:hidden!important;white-space:normal!important;contain:layout paint!important}
#lv:not([hidden]) #stg.stage>.rima-beat-frame{position:absolute!important;inset:5px!important;z-index:0!important;display:block!important;box-sizing:border-box!important;border:1.5px solid rgba(237,195,77,.42)!important;border-radius:17px!important;opacity:.5!important;pointer-events:none!important;transform:scale(1)!important;transform-origin:center!important;box-shadow:0 0 10px rgba(237,195,77,.12),inset 0 0 10px rgba(237,195,77,.045)!important;will-change:transform,opacity,box-shadow,border-color!important}
#pbar .pwi{flex:1 1 0!important;min-width:0!important;max-width:none!important;overflow:hidden!important}
#pbar #pwn{display:block!important;position:relative!important;width:100%!important;min-width:0!important;max-width:none!important;overflow:hidden!important;white-space:nowrap!important;text-overflow:clip!important}
#pbar #pwn .rima-title-track{display:inline-flex!important;width:max-content!important;max-width:none!important;white-space:nowrap!important;align-items:center!important;flex-wrap:nowrap!important;will-change:transform!important}
#pbar #pwn .rima-title-track>span{display:inline-block!important;width:max-content!important;max-width:none!important;flex:0 0 auto!important;white-space:nowrap!important}
#pbar #pwn .rima-title-track>i{display:block!important;width:76px!important;min-width:76px!important;flex:0 0 76px!important;height:1px!important}
#pbar #pwn .rima-title-track.is-long{animation:rima-title-marquee-v69 linear infinite!important}
#pbar #pwn .rima-title-track:not(.is-long){animation:none!important}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{margin:0!important;padding:0!important;text-indent:0!important}
</style>'''+h[b+8:]
# Clean unusual Unicode spaces in the favorite card title at its rendering source.
old="const title=esc(rimaV59CleanTitle(t.x[1]||'')),artist="
new="const title=esc(String(rimaV59CleanTitle(t.x[1]||'')).replace(/[\\u2000-\\u200F\\u2028-\\u202F\\u205F\\u3000\\uFEFF]/g,' ').replace(/[\\s\\u00A0]+/gu,' ').trim()),artist="
if h.count(old)!=1: raise SystemExit('V72_FAIL: título dos favoritos não encontrado')
h=h.replace(old,new,1)
# Re-arm the word clock after audio analysis resolves in a restarted live stage.
insert='''<script id="rimalab-stage-wordclock-restart-v72">
(function(){
 const old=window.zDone;
 if(typeof old!=='function'||old.__rimaV72)return;
 const wrapped=function(){
  const result=old.apply(this,arguments),live=document.getElementById('lv');
  if(live&&!live.hidden&&window.play&&window.ZS&&!ZS.dp){
   if(typeof WD==='undefined'||!WD)wInit();
   if(typeof WD!=='undefined'&&WD&&WD.ph===0)wStart();
  }
  return result;
 };
 wrapped.__rimaV72=true;window.zDone=wrapped;
})();
</script>
'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V72_FAIL: body ausente')
h=h[:pos]+insert+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='91': raise SystemExit('V72_FAIL: versionCode base incorreto')
g=g[:m.start(1)]+'92'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.9': raise SystemExit('V72_FAIL: versionName base incorreto')
g=g[:m.start(1)]+'3.5.0'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V72_OK: pulse restored, responsive stage, restart-safe word clock, clean favorite title; 3.5.0/code92')
