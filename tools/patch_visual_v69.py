#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V69_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-player-marquee-favorites-status-v69' in h: raise SystemExit('V69_FAIL: patch já aplicado')
old="const fail=()=>{if(my!=zTok)return;ZS.loadingAudio=0;if(fall)fall();else zMsg('Não consegui abrir esse arquivo de áudio.')};"
new="const fail=()=>{if(my!=zTok)return;ZS.loadingAudio=0;if(fall)fall();zMsg('Esse beat não abriu. Escolha outra faixa.');};"
if h.count(old)!=1: raise SystemExit('V69_FAIL: handler de falha do carregamento não encontrado')
h=h.replace(old,new,1)
# A single marquee track with an explicit trailing gap before its duplicate.
old="""function ticker(){
 const e=$('#pwn');if(!e||!window.ZS)return;const name=String(ZS.name||'Beat');if(e.dataset.rimaTitle===name)return;
 e.dataset.rimaTitle=name;e.innerHTML='<span class="rima-title-track"><span>'+esc(name)+'</span><span aria-hidden="true">'+esc(name)+'</span></span>';
 const track=e.firstElementChild;requestAnimationFrame(()=>{if(!track||!e.isConnected)return;const long=track.firstElementChild.scrollWidth>e.clientWidth+12;track.classList.toggle('is-long',long);if(long)track.style.animationDuration=Math.max(10,Math.min(24,track.scrollWidth/38))+'s'});
}"""
new="""function ticker(){
 const e=$('#pwn');if(!e||!window.ZS)return;const name=String(ZS.name||'Beat');if(e.dataset.rimaTitle===name&&e.querySelector('.rima-title-track'))return;
 e.dataset.rimaTitle=name;
 const safe=esc(name);
 e.innerHTML='<span class="rima-title-track"><span>'+safe+'</span><i aria-hidden="true"></i><span aria-hidden="true">'+safe+'</span><i aria-hidden="true"></i></span>';
 const track=e.firstElementChild;
 const measure=()=>{if(!track||!e.isConnected)return;const first=track.children[0],gap=track.children[1];if(!first||!gap)return;const long=first.getBoundingClientRect().width>e.clientWidth+8;track.classList.toggle('is-long',long);track.style.animationDuration=long?Math.max(9,Math.min(25,(first.getBoundingClientRect().width+76)/34))+'s':'0s'};
 requestAnimationFrame(measure);
}"""
if h.count(old)!=1: raise SystemExit('V69_FAIL: função marquee original não encontrada')
h=h.replace(old,new,1)
css=r'''<style id="rimalab-player-marquee-favorites-status-v69">
/* Failure replaces the loading status; it must never remain "Abrindo..." after rejection. */
#pbar .pwi{display:block!important;flex:1 1 0!important;min-width:0!important;max-width:100%!important;overflow:hidden!important}
#pbar #pwn{display:block!important;position:relative!important;width:100%!important;min-width:0!important;max-width:100%!important;overflow:hidden!important;white-space:nowrap!important;text-overflow:clip!important}
#pbar #pwn .rima-title-track{display:inline-flex!important;align-items:center!important;gap:0!important;width:max-content!important;max-width:none!important;white-space:nowrap!important;will-change:transform}
#pbar #pwn .rima-title-track>span{display:inline-block!important;flex:none!important;white-space:nowrap!important}
#pbar #pwn .rima-title-track>i{display:block!important;flex:0 0 76px!important;width:76px!important;height:1px!important}
#pbar #pwn .rima-title-track.is-long{animation:rima-title-marquee-v69 linear infinite!important}
@keyframes rima-title-marquee-v69{from{transform:translateX(0)}to{transform:translateX(-50%)}}
/* Favorite titles use the same typography scale and card proportions as category beat rows. */
#bp .rima-v43-fav-row>.beat-info,#bq .rima-v43-fav-row>.beat-info,#bbq .rima-v43-fav-row>.beat-info{
 display:flex!important;flex-direction:column!important;gap:3px!important;min-width:0!important
}
#bp .rima-v43-fav-play,#bq .rima-v43-fav-play,#bbq .rima-v43-fav-play{
 min-height:50px!important;height:auto!important;padding:9px 12px 3px!important;
 border-radius:14px 14px 0 0!important;font-family:'Archivo',Arial,sans-serif!important;
 font-size:15px!important;line-height:1.2!important
}
#bp .rima-v43-fav-play b,#bq .rima-v43-fav-play b,#bbq .rima-v43-fav-play b{
 display:-webkit-box!important;-webkit-box-orient:vertical!important;-webkit-line-clamp:2!important;
 overflow:hidden!important;font-family:'Archivo',Arial,sans-serif!important;
 font-size:15px!important;font-weight:750!important;line-height:1.2!important;
 letter-spacing:-.015em!important
}
#bp .rima-v43-fav-row .beat-meta,#bq .rima-v43-fav-row .beat-meta,#bbq .rima-v43-fav-row .beat-meta{
 display:flex!important;align-items:center!important;gap:8px!important;
 padding:4px 10px 0!important;font-size:12px!important;line-height:1.2!important
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V69_FAIL: body ausente')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='88': raise SystemExit('V69_FAIL: versionCode base não é 88')
g=g[:m.start(1)]+'89'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.6': raise SystemExit('V69_FAIL: versionName base não é 3.4.6')
g=g[:m.start(1)]+'3.4.7'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V69_OK: load failure status replaces opening; seamless title marquee with trailing gap; favorites typography normalized; 3.4.7/code89')
