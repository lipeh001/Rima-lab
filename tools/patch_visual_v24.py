#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# O modo Palavras não exibe mais a linha textual "Rimas possíveis".
old="sub:'Rimas possíveis: '+r"
if old in h:
    h=h.replace(old,"sub:''",1)
elif "sub:''" not in h:
    raise SystemExit('V24_FAIL: descrição de rimas do modo Palavras não encontrada')
# Protege contra a versão alternativa em que a descrição é montada fora do objeto.
h=h.replace("$('#cs').textContent=c.sub;","$('#cs').textContent=(B&&B.mode==='pal')?'':(c.sub||'');")

# RAPPER é pronunciado com tonicidade inicial em português brasileiro; não sugerir rimas oxítonas genéricas.
marker="const RIMA_NO_HINTS_V24=new Set(['RAPPER']);"
if marker not in h:
    anchor="const rimasDe=w=>{"
    if anchor not in h: raise SystemExit('V24_FAIL: função rimasDe não encontrada')
    h=h.replace(anchor,marker+"\n"+anchor+"if(RIMA_NO_HINTS_V24.has(String(w||'').trim().toUpperCase()))return'';",1)

# Ajuste de palco: reservar altura para acentos e evitar que palavras longas encostem/cortem no topo.
css=r"""<style id="rimalab-word-vertical-fit-v24">
#stg.stage #cb{
 box-sizing:border-box!important;
 padding:22px 8px 18px!important;
 line-height:1.12!important;
 max-height:38vh!important;
 overflow:visible!important;
 vertical-align:middle!important;
}
#stg.stage #cs:empty{display:none!important}
#stg.stage #rm:empty{display:none!important}
</style>
<script id="rimalab-word-vertical-fit-script-v24">
(function(){
 const fit=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!e||!stage||!e.textContent.trim())return;
  const raw=e.textContent.trim();
  const available=Math.max(100,stage.clientWidth-52);
  const height=Math.max(54,Math.min(stage.clientHeight*.34,190));
  const cap=raw.length>14?66:raw.length>10?76:raw.length>7?88:100;
  e.style.setProperty('white-space','nowrap','important');
  e.style.setProperty('word-break','normal','important');
  e.style.setProperty('overflow-wrap','normal','important');
  e.style.setProperty('line-height','1.12','important');
  let low=24,high=cap;
  for(let i=0;i<14;i++){
   const mid=(low+high)/2;
   e.style.setProperty('font-size',mid.toFixed(1)+'px','important');
   if(e.scrollWidth<=available&&e.getBoundingClientRect().height<=height)low=mid;else high=mid;
  }
  e.style.setProperty('font-size',Math.floor(low)+'px','important');
 };
 const boot=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!e||!stage)return;
  new MutationObserver(fit).observe(e,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize',fit,{passive:true});
  window.addEventListener('orientationchange',()=>setTimeout(fit,120),{passive:true});
  fit();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>"""
if 'id="rimalab-word-vertical-fit-v24"' not in h:
    pos=h.lower().rfind('</body>')
    if pos<0: raise SystemExit('V24_FAIL: fechamento do body não encontrado')
    h=h[:pos]+css+'\n'+h[pos:]

# Paisagem: palco e controles menores, player com barra de posição visível e utilizável.
land=r"""<style id="rimalab-landscape-player-v24">
@media (orientation:landscape) and (max-height:850px){
 body.pl main{padding-bottom:calc(142px + env(safe-area-inset-bottom,0px))!important}
 #lv:not([hidden]){grid-template-columns:minmax(0,1.45fr) minmax(0,1fr)!important;gap:7px 10px!important;align-items:stretch!important}
 #lv>.stage{min-height:0!important;height:clamp(150px,calc(100svh - 190px),430px)!important;max-height:calc(100svh - 190px)!important;padding:12px!important;overflow:hidden!important}
 #lv>.stage #cb{max-height:30vh!important;padding:14px 6px 12px!important}
 #lv>.bk,#lv>.card:not(.stage),#lv>.btn.w{min-width:0!important}
 #pbar{left:10px!important;right:10px!important;bottom:calc(52px + env(safe-area-inset-bottom,0px))!important;height:78px!important;min-height:78px!important;padding:5px 9px 23px!important;display:flex!important;flex-direction:row!important;align-items:center!important;gap:7px!important}
 #pbar .pwrow{min-width:0!important;flex:1 1 auto!important;min-height:38px!important;gap:5px!important}
 #pbar .pw-art{display:none!important}
 #pbar .pw-controls{flex:0 0 auto!important;gap:1px!important}
 #pbar .pw-controls button{width:27px!important;height:30px!important}
 #pbar .pw-controls #pwb{width:34px!important;height:34px!important}
 #pbar .pwi{min-width:0!important;flex:1 1 auto!important}
 #pbar .pwi b{font-size:11px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
 #pbar .pwi small{display:none!important}
 #pbar .pws{width:26px!important;height:26px!important;flex:0 0 26px!important}
 #pbar .pwinfo{display:block!important;position:absolute!important;right:10px!important;bottom:5px!important;font-size:9px!important}
 #pbar .pwscr{display:flex!important;visibility:visible!important;position:absolute!important;left:12px!important;right:78px!important;bottom:6px!important;height:8px!important;min-height:8px!important;z-index:9!important}
 #pbar .pwscr input[type=range],#pbar .pwscr input{display:block!important;visibility:visible!important;width:100%!important;min-width:0!important;height:7px!important;opacity:1!important;pointer-events:auto!important;accent-color:#edc34d!important}
 nav{z-index:100!important;min-height:48px!important;padding:2px 8px calc(2px + env(safe-area-inset-bottom,0px))!important}
 nav button{min-height:42px!important}
}
@media (orientation:landscape) and (max-height:500px){
 #lv>.stage{height:calc(100svh - 160px)!important;max-height:calc(100svh - 160px)!important}
 #pbar{height:70px!important;min-height:70px!important}
}
</style>"""
if 'id="rimalab-landscape-player-v24"' not in h:
    pos=h.lower().rfind('</body>')
    h=h[:pos]+land+'\n'+h[pos:]

# Restore visual beat pulse after Android returns from another app: resume WebAudio contexts without restarting playback.
life=r"""<script id="rimalab-resume-audio-v24">
(function(){
 let last=0;
 const resume=()=>{
  const now=Date.now();if(now-last<300)return;last=now;
  try{
   const contexts=[];
   for(const k of Object.keys(window)){
    let v;try{v=window[k]}catch(e){}
    if(v&&typeof v==='object'&&typeof v.resume==='function'&&typeof v.state==='string'&&v.state==='suspended'&&typeof v.currentTime==='number')contexts.push(v);
   }
   contexts.forEach(c=>{try{const p=c.resume();if(p&&p.catch)p.catch(()=>{})}catch(e){}});
  }catch(e){}
 };
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)resume()});
 window.addEventListener('pageshow',resume);
 window.addEventListener('focus',resume);
})();
</script>"""
if 'id="rimalab-resume-audio-v24"' not in h:
    pos=h.lower().rfind('</body>')
    h=h[:pos]+life+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+43\b',g):
    g=re.sub(r'\bversionCode\s+43\b','versionCode 44',g,count=1)
elif not re.search(r'\bversionCode\s+44\b',g):
    raise SystemExit('V24_FAIL: versionCode inesperado')
if "versionName '3.0.1'" in g:g=g.replace("versionName '3.0.1'","versionName '3.0.2'",1)
elif "versionName '3.0.2'" not in g:raise SystemExit('V24_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V24_OK: modo palavras limpo; palavra sem corte; seekbar horizontal; áudio retomado')
