#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
p=root/'app/src/main/assets/rima-lab.html'
s=p.read_text(encoding='utf-8')

# Reset previously auto-inferred WebView latency once; it is not a measurement of speaker/Bluetooth delay.
old="if(localStorage.getItem('rimalab_lat_reset_v1')!=='1'){localStorage.removeItem('lat');localStorage.setItem('rimalab_lat_reset_v1','1')}"
new="if(localStorage.getItem('rimalab_lat_reset_v2')!=='1'){localStorage.removeItem('lat');localStorage.setItem('rimalab_lat_reset_v2','1')}"
if old in s:s=s.replace(old,new,1)
elif "rimalab_lat_reset_v2" not in s:raise SystemExit('V15_FAIL: marcador de reset de latência não encontrado')

# WebView outputLatency/baseLatency are internal pipeline values; they cannot identify Bluetooth routing.
cal=r"""async function cal(){if(CAL_RUN)return;const run={cancelled:false,timer:null,sources:new Set()};CAL_RUN=run;const ms=t=>$$('.cm').forEach(e=>e.textContent=t),start=$('#cal-start'),stopBtn=$('#cal-stop');if(start){start.disabled=true;start.textContent='Ajustando...'}if(stopBtn)stopBtn.hidden=true;try{if(play)stop();setLat(0);ms('Saída pelo alto-falante do celular: 0 ms de compensação. O Android/WebView não consegue medir automaticamente o atraso acústico nem identificar com segurança uma caixa Bluetooth. Se ouvir atraso, use o ajuste manual.')}catch(e){setLat(0);ms('Compensação zerada. A medição automática não está disponível neste aparelho; use o ajuste manual somente se perceber atraso.')}finally{if(CAL_RUN===run)CAL_RUN=null;if(start){start.disabled=false;start.textContent='Calibrar (opcional)'}if(stopBtn)stopBtn.hidden=true}}
const CH="""
s,n=re.subn(r"async function cal\(\)\{.*?\}\s*const CH=",cal,s,count=1,flags=re.S)
if n!=1:raise SystemExit('V15_FAIL: função cal() não encontrada para substituir')

# The beat timer is the audio-output clock. Retrigger both frame and word pulses on every scheduled beat.
pulse=r"""function pulse(q){if(CNT&&q>0){const e=$('#lv').hidden?($('#sb')||(B&&B.cin?$('#cd'):null)):$('#cb');if(e){e.textContent=4-q;e.style.fontSize='96px';stamp(e)}}$$('.dots').forEach(c=>[...c.children].forEach((d,j)=>d.classList.toggle('on',j==q)));const stage=$('#lv').hidden?null:$('#stg');const targets=[stage,...$$('#bt .stage')].filter(Boolean);targets.forEach(e=>{e.classList.remove('hit');void e.offsetWidth;e.classList.add('hit');clearTimeout(e.__rimaBeatTimer);e.__rimaBeatTimer=setTimeout(()=>e.classList.remove('hit'),420)});const word=stage?$('#cb'):null;if(word){word.classList.remove('beat-word-hit');void word.offsetWidth;word.classList.add('beat-word-hit');clearTimeout(word.__rimaWordBeatTimer);word.__rimaWordBeatTimer=setTimeout(()=>word.classList.remove('beat-word-hit'),420)}}"""
s,n=re.subn(r"function pulse\(q\)\{.*?\}\s*function start\(\)",pulse+"\nfunction start()",s,count=1,flags=re.S)
if n!=1:raise SystemExit('V15_FAIL: função pulse() não encontrada para substituir')

style=r'''<style id="rimalab-visual-v15">
/* Recupera o impacto dourado do palco: brilho da moldura + pulso da palavra no mesmo tick do áudio. */
#stg.stage,#bt .stage{position:relative!important;isolation:isolate!important;overflow:hidden!important}
#stg.stage.hit,#bt .stage.hit{
 border-color:rgba(255,218,112,.98)!important;
 box-shadow:0 0 0 1px rgba(237,195,77,.24),0 0 34px rgba(237,195,77,.34),inset 0 0 34px rgba(237,195,77,.13)!important;
}
#stg.stage::after,#bt .stage::after{
 content:""!important;display:block!important;position:absolute!important;inset:1px!important;z-index:4!important;
 pointer-events:none!important;border:1px solid rgba(237,195,77,.2)!important;border-radius:inherit!important;
 opacity:.22!important;box-shadow:inset 0 0 18px rgba(237,195,77,.07),0 0 12px rgba(237,195,77,.06)!important;
}
#stg.stage.hit::after,#bt .stage.hit::after{animation:rimalab-frame-impact-v15 .42s ease-out!important}
@keyframes rimalab-frame-impact-v15{
 0%{opacity:1;border-color:rgba(255,231,160,1)!important;box-shadow:inset 0 0 38px rgba(237,195,77,.27),0 0 38px rgba(237,195,77,.38)!important}
 100%{opacity:.2;border-color:rgba(237,195,77,.2)!important;box-shadow:inset 0 0 8px rgba(237,195,77,.025),0 0 6px rgba(237,195,77,.025)!important}
}
#stg.stage #cb,#bt .stage .word{
 color:#edc34d!important;text-shadow:0 0 20px rgba(237,195,77,.2)!important;
 transform-origin:center!important;will-change:transform,filter,text-shadow!important;
}
#stg.stage #cb.beat-word-hit,#bt .stage .word.beat-word-hit{
 color:#fff0bd!important;
 text-shadow:0 0 10px rgba(255,238,184,.95),0 0 28px rgba(237,195,77,.78),0 0 54px rgba(237,195,77,.42)!important;
 animation:rimalab-word-impact-v15 .42s cubic-bezier(.16,1,.3,1)!important;
}
@keyframes rimalab-word-impact-v15{
 0%{transform:scale(.94);filter:brightness(1.55)}
 58%{transform:scale(1.055);filter:brightness(1.28)}
 100%{transform:scale(1);filter:brightness(1)}
}
/* Large default word; only reduce when the actual rendered glyph width exceeds the stage. */
#stg.stage #cb{
 display:block!important;box-sizing:border-box!important;width:100%!important;max-width:100%!important;
 margin:12px auto!important;padding:8px 6px!important;text-align:center!important;
 font-family:Anton,Impact,"Arial Narrow",sans-serif!important;font-size:112px!important;
 font-weight:900!important;line-height:1.02!important;letter-spacing:-.045em!important;
 white-space:nowrap!important;word-break:normal!important;overflow-wrap:normal!important;
}
@media(prefers-reduced-motion:reduce){
 #stg.stage.hit::after,#bt .stage.hit::after,#stg.stage #cb.beat-word-hit,#bt .stage .word.beat-word-hit{animation:none!important}
}
</style>
<script id="rima-word-fit-script-v15">
(function(){
 const fit=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!e||!stage)return;
  const raw=(e.textContent||'').trim();if(!raw)return;
  const available=Math.max(120,stage.clientWidth-52);
  const measure=()=>{
   try{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().width}
   catch(_){return e.scrollWidth}
  };
  e.style.setProperty('font-size','112px','important');
  if(measure()<=available)return;
  let lo=34,hi=112;
  for(let i=0;i<16;i++){const mid=(lo+hi)/2;e.style.setProperty('font-size',mid.toFixed(1)+'px','important');if(measure()<=available)lo=mid;else hi=mid}
  e.style.setProperty('font-size',Math.floor(lo)+'px','important');
 };
 const boot=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');if(!e||!stage)return;
  new MutationObserver(fit).observe(e,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize',fit,{passive:true});fit();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>'''
if 'id="rimalab-visual-v15"' not in s:
 pos=s.lower().rfind('</body>')
 if pos<0:raise SystemExit('V15_FAIL: </body> não encontrado')
 s=s[:pos]+style+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')

gp=root/'app/build.gradle'
g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+33\b',g):g=re.sub(r'\bversionCode\s+33\b','versionCode 34',g,count=1)
elif not re.search(r'\bversionCode\s+34\b',g):raise SystemExit('V15_FAIL: versionCode inesperado')
if "versionName '2.9.6'" in g:g=g.replace("versionName '2.9.6'","versionName '2.9.7'",1)
elif "versionName '2.9.7'" not in g:raise SystemExit('V15_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V15_OK: palco dourado forte, palavra grande adaptativa e calibração sem falsa latência')
