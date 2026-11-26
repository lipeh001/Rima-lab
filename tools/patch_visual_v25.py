#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
css=r"""<style id="rimalab-word-finish-v25">
#lv:not([hidden])>.bk{margin-top:16px!important;margin-bottom:16px!important;align-self:flex-start!important}
#lv:not([hidden]) #stg.stage #rm>*{font-size:clamp(17px,4.2vw,27px)!important;line-height:1.12!important;padding:8px 15px!important}
#lv:not([hidden]) #stg.stage #cb .rima-curve-char{display:inline-block!important;transform:translateY(var(--rima-curve-y,0px))!important;transform-origin:50% 100%!important}
</style>
<script id="rimalab-word-finish-script-v25">
(function(){
 const curve=()=>{
  const e=document.getElementById('cb');if(!e)return;
  const raw=(e.textContent||'').trim();if(!raw||e.dataset.rimaCurveText===raw)return;
  e.dataset.rimaCurveText=raw;
  const chars=Array.from(raw),mid=(chars.length-1)/2,arc=Math.min(4.5,Math.max(1.8,chars.length*.22)),frag=document.createDocumentFragment();
  chars.forEach((ch,i)=>{
   const span=document.createElement('span');span.className='rima-curve-char';span.textContent=ch===' '?'\u00a0':ch;
   const d=mid?Math.abs(i-mid)/mid:0;span.style.setProperty('--rima-curve-y',(-arc*(1-d*d)).toFixed(2)+'px');frag.appendChild(span);
  });
  e.replaceChildren(frag);
 };
 const fitHints=()=>{
  const word=document.getElementById('cb'),hints=document.getElementById('rm');if(!word||!hints)return;
  const main=parseFloat(getComputedStyle(word).fontSize)||60,size=Math.max(16,Math.min(29,main*.46));
  hints.querySelectorAll(':scope > *').forEach(el=>{el.style.setProperty('font-size',Math.min(size,main*.54).toFixed(1)+'px','important');el.style.setProperty('line-height','1.12','important')});
 };
 const boot=()=>{
  const word=document.getElementById('cb'),stage=document.getElementById('stg');if(!word||!stage)return;
  const update=()=>{curve();fitHints()};
  new MutationObserver(update).observe(word,{childList:true,subtree:true,characterData:true});
  const hints=document.getElementById('rm');if(hints)new MutationObserver(fitHints).observe(hints,{childList:true,subtree:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(fitHints).observe(stage);
  window.addEventListener('resize',fitHints,{passive:true});window.addEventListener('orientationchange',()=>setTimeout(fitHints,100),{passive:true});update();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>"""
if 'id="rimalab-word-finish-v25"' not in h:
 pos=h.lower().rfind('</body>')
 if pos<0:raise SystemExit('V25_FAIL: </body> não encontrado')
 h=h[:pos]+css+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+44\b',g):g=re.sub(r'\bversionCode\s+44\b','versionCode 45',g,count=1)
elif not re.search(r'\bversionCode\s+45\b',g):raise SystemExit('V25_FAIL: versionCode inesperado')
if "versionName '3.0.2'" in g:g=g.replace("versionName '3.0.2'","versionName '3.0.3'",1)
elif "versionName '3.0.3'" not in g:raise SystemExit('V25_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V25_OK: botão voltar equilibrado; dicas maiores e subordinadas; palavra com arco ascendente sutil')
