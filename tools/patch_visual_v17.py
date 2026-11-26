#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
h=hp.read_text(encoding='utf-8')
if 'id="rimalab-visual-v17"' not in h:
    style=r"""<style id="rimalab-visual-v17">
/* v18: palco com geometria fixa; somente o contorno interno pulsa sem alterar layout. */
#stg.stage{
  box-sizing:border-box!important;
  transform:none!important;
  animation:none!important;
  transition:none!important;
}
#stg.stage.hit{
  transform:none!important;
  animation:none!important;
  border-color:rgba(237,195,77,.62)!important;
  box-shadow:0 0 0 1px rgba(237,195,77,.10),0 0 12px rgba(237,195,77,.12),inset 0 0 12px rgba(237,195,77,.035)!important;
}
#stg.stage::after{
  inset:3px!important;
  transform:scale(1)!important;
  transform-origin:center center!important;
  border-width:1.5px!important;
  opacity:.34!important;
  box-shadow:0 0 9px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important;
}
#stg.stage.hit::after{
  animation:rimalab-frame-only-v18 .34s cubic-bezier(.2,.75,.25,1)!important;
}
@keyframes rimalab-frame-only-v18{
  0%{opacity:.48;transform:scale(1);border-color:rgba(237,195,77,.48)!important;box-shadow:0 0 10px rgba(237,195,77,.12),inset 0 0 8px rgba(237,195,77,.035)!important}
  42%{opacity:.88;transform:scale(1.012);border-color:rgba(255,220,126,.88)!important;box-shadow:0 0 18px rgba(237,195,77,.22),inset 0 0 9px rgba(237,195,77,.05)!important}
  100%{opacity:.34;transform:scale(1);border-color:rgba(237,195,77,.34)!important;box-shadow:0 0 9px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important}
}
/* O palco e o texto nunca participam da escala. Só o pseudo-elemento da moldura se move. */
#stg.stage #cb,
#stg.stage #cb.beat-word-hit{
  animation:none!important;
  transform:none!important;
  filter:none!important;
  transition:none!important;
  letter-spacing:.015em!important;
  font-kerning:normal!important;
  font-variant-ligatures:none!important;
  font-stretch:normal!important;
  text-shadow:0 0 4px rgba(237,195,77,.10)!important;
}
@media(prefers-reduced-motion:reduce){
 #stg.stage.hit::after{animation:none!important;opacity:.34!important;transform:scale(1)!important}
}
#stg.stage{
  position:relative!important;
  overflow:visible!important;
  isolation:isolate!important;
  box-sizing:border-box!important;
}
#stg.stage::after{
  content:""!important;
  display:block!important;
  position:absolute!important;
  inset:-6px!important;
  z-index:5!important;
  pointer-events:none!important;
  border:1.5px solid rgba(237,195,77,.42)!important;
  border-radius:inherit!important;
  opacity:.42!important;
  transform:scale(.99)!important;
  transform-origin:center!important;
  box-shadow:0 0 12px rgba(237,195,77,.13),inset 0 0 12px rgba(237,195,77,.05)!important;
}
#stg.stage.hit::after{
  animation:rimalab-frame-only-v17 .34s cubic-bezier(.2,.75,.25,1)!important;
}
@keyframes rimalab-frame-only-v17{
  0%{opacity:.95;transform:scale(.99);border-color:rgba(255,231,160,.95)!important;box-shadow:0 0 22px rgba(237,195,77,.32),0 0 36px rgba(237,195,77,.16),inset 0 0 12px rgba(237,195,77,.08)!important}
  55%{opacity:.8;transform:scale(1.025);border-color:rgba(255,220,126,.85)!important;box-shadow:0 0 25px rgba(237,195,77,.3),0 0 42px rgba(237,195,77,.15)!important}
  100%{opacity:.42;transform:scale(.99);border-color:rgba(237,195,77,.42)!important;box-shadow:0 0 12px rgba(237,195,77,.13),inset 0 0 12px rgba(237,195,77,.05)!important}
}
/* Neutraliza qualquer pulso/brilho aplicado diretamente à palavra. */
#stg.stage #cb,
#stg.stage #cb.beat-word-hit{
  animation:none!important;
  transform:none!important;
  filter:none!important;
  color:#edc34d!important;
  text-shadow:0 0 5px rgba(237,195,77,.12)!important;
  transition:none!important;
}
/* Palco mantém sua geometria; a tipografia se adapta ao espaço interno. */
#stg.stage #cb{
  display:block!important;
  box-sizing:border-box!important;
  width:100%!important;
  max-width:100%!important;
  padding:8px 8px!important;
  margin:12px auto!important;
  text-align:center!important;
  white-space:nowrap!important;
  line-height:1.04!important;
  letter-spacing:.005em!important;
  font-kerning:normal!important;
  transform-origin:center!important;
}
@media(prefers-reduced-motion:reduce){
 #stg.stage.hit::after{animation:none!important;opacity:.42!important}
}
</style>
<script id="rimalab-word-fit-v17">
(function(){
 const fit=()=>{
  const word=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!word||!stage)return;
  const value=(word.textContent||'').trim();
  if(!value)return;
  const length=[...value].length;
  const base=length<=5?88:length<=8?98:108;
  const available=Math.max(120,stage.clientWidth-64);
  const measure=()=>{
   try{const range=document.createRange();range.selectNodeContents(word);return range.getBoundingClientRect().width}
   catch(_){return word.scrollWidth}
  };
  word.style.setProperty('font-size',base+'px','important');
  if(measure()<=available)return;
  let low=32,high=base;
  for(let i=0;i<18;i++){
   const mid=(low+high)/2;
   word.style.setProperty('font-size',mid.toFixed(1)+'px','important');
   if(measure()<=available)low=mid;else high=mid;
  }
  word.style.setProperty('font-size',Math.floor(low)+'px','important');
 };
 const init=()=>{
  const word=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!word||!stage)return;
  if(word.__rimaFitV17)return;
  word.__rimaFitV17=true;
  new MutationObserver(fit).observe(word,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(fit).observe(stage);
  window.addEventListener('resize',fit,{passive:true});
  fit();
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
</script>"""
    pos=h.lower().rfind('</body>')
    if pos<0: raise SystemExit('V17_FAIL: </body> não encontrado')
    h=h[:pos]+style+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')
gp=root/'app/build.gradle'
g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+35\b',g): g=re.sub(r'\bversionCode\s+35\b','versionCode 37',g,count=1)
elif not re.search(r'\bversionCode\s+36\b',g): raise SystemExit('V17_FAIL: versionCode inesperado')
if "versionName '2.9.8'" in g: g=g.replace("versionName '2.9.8'","versionName '2.9.10'",1)
elif "versionName '2.9.9'" not in g: raise SystemExit('V17_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V18_OK: palco e palavra estáticos; moldura pulsa apenas 1,2% sem alterar layout')
