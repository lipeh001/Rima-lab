#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# Replace the beat callback so the hit is sent only to the stage frame.
pattern=r'function pulse\(q\)\{.*?\}(?=\s*function start\()'
m=re.search(pattern,h,re.S)
if not m:
    raise SystemExit('V18_FAIL: função pulse(q) não encontrada')
new_pulse="""function pulse(q){if(CNT&&q>0){const e=$('#lv').hidden?($('#sb')||(B&&B.cin?$('#cd'):null)):$('#cb');if(e){e.textContent=4-q;e.style.fontSize='96px';stamp(e)}}$$('.dots').forEach(c=>[...c.children].forEach((d,j)=>d.classList.toggle('on',j==q)));const stage=$('#lv').hidden?null:$('#stg');const targets=[stage,...$$('#bt .stage')].filter(Boolean);targets.forEach(e=>{e.classList.remove('hit');void e.offsetWidth;e.classList.add('hit');clearTimeout(e.__rimaBeatTimer);e.__rimaBeatTimer=setTimeout(()=>e.classList.remove('hit'),420)})}"""
h=h[:m.start()]+new_pulse+h[m.end():]

style=r"""
<style id="rimalab-visual-v18">
/* Geometria do palco travada: a palavra não pode redimensionar o cartão. */
#lv:not([hidden]) #stg.stage{
  box-sizing:border-box!important;
  width:100%!important;
  height:360px!important;
  min-height:360px!important;
  max-height:360px!important;
  flex:0 0 360px!important;
  min-width:0!important;
  position:relative!important;
  overflow:hidden!important;
  transform:none!important;
  transition:none!important;
  animation:none!important;
}
/* O texto e todo o conteúdo ficam imóveis durante o pulso. */
#lv:not([hidden]) #stg.stage #cb,
#lv:not([hidden]) #stg.stage #cb.beat-word-hit{
  transform:none!important;
  animation:none!important;
  filter:none!important;
  transition:none!important;
}
/* Só a moldura interna recebe o pulso: cresce e retorna sem alterar o layout. */
#lv:not([hidden]) #stg.stage::after{
  content:""!important;
  display:block!important;
  position:absolute!important;
  inset:5px!important;
  z-index:6!important;
  pointer-events:none!important;
  box-sizing:border-box!important;
  border:1.5px solid rgba(237,195,77,.42)!important;
  border-radius:inherit!important;
  opacity:.36!important;
  transform:scale(1)!important;
  transform-origin:center!important;
  box-shadow:0 0 10px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important;
}
#lv:not([hidden]) #stg.stage.hit{
  transform:none!important;
  border-color:rgba(237,195,77,.62)!important;
  box-shadow:0 0 0 1px rgba(237,195,77,.10),0 0 12px rgba(237,195,77,.12),inset 0 0 12px rgba(237,195,77,.035)!important;
}
#lv:not([hidden]) #stg.stage.hit::after{
  animation:rimalab-frame-impact-v18 .34s cubic-bezier(.2,.75,.25,1)!important;
}
@keyframes rimalab-frame-impact-v18{
  0%{
    opacity:.42;
    transform:scale(1);
    border-color:rgba(237,195,77,.48)!important;
    box-shadow:0 0 10px rgba(237,195,77,.12),inset 0 0 8px rgba(237,195,77,.035)!important;
  }
  42%{
    opacity:.95;
    transform:scale(1.035);
    border-color:rgba(255,224,142,.98)!important;
    box-shadow:0 0 22px rgba(237,195,77,.30),0 0 34px rgba(237,195,77,.16),inset 0 0 12px rgba(237,195,77,.06)!important;
  }
  100%{
    opacity:.36;
    transform:scale(1);
    border-color:rgba(237,195,77,.42)!important;
    box-shadow:0 0 10px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important;
  }
}
@media(prefers-reduced-motion:reduce){
  #lv:not([hidden]) #stg.stage.hit::after{
    animation:none!important;
    opacity:.36!important;
    transform:scale(1)!important;
  }
}
</style>
"""
if 'id="rimalab-visual-v18"' in h:
    h=re.sub(r'<style id="rimalab-visual-v18">.*?</style>','',h,flags=re.S)
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V18_FAIL: </body> não encontrado')
h=h[:pos]+style+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+37\b',g):
    g=re.sub(r'\bversionCode\s+37\b','versionCode 38',g,count=1)
elif not re.search(r'\bversionCode\s+38\b',g):
    raise SystemExit('V18_FAIL: versionCode inesperado')
if "versionName '2.9.10'" in g:
    g=g.replace("versionName '2.9.10'","versionName '2.9.11'",1)
elif "versionName '2.9.11'" not in g:
    raise SystemExit('V18_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V18_OK: palco fixo 360px; somente moldura pulsa 3,5%; palavra sem animação')
