#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# A palavra pode mudar de conteúdo/tamanho, mas isso nunca aciona a moldura.
# O único gatilho da moldura é pulse(q), chamado pelo relógio do beat.
frame=r"""function rimaPulseStageFrame(){
 const stage=document.getElementById('stg');
 const screen=document.getElementById('lv');
 if(!stage||!screen||screen.hidden)return;
 let frame=stage.querySelector(':scope > .rima-beat-frame');
 if(!frame){
  frame=document.createElement('span');
  frame.className='rima-beat-frame';
  frame.setAttribute('aria-hidden','true');
  stage.insertBefore(frame,stage.firstChild);
 }
 if(frame.__rimaPulseRAF)cancelAnimationFrame(frame.__rimaPulseRAF);
 const started=performance.now(),duration=210;
 const baseShadow='0 0 12px rgba(237,195,77,.22),inset 0 0 9px rgba(237,195,77,.08)';
 const peakShadow='0 0 25px rgba(255,220,126,.58),0 0 44px rgba(237,195,77,.34),inset 0 0 15px rgba(237,195,77,.12)';
 const draw=now=>{
  const p=Math.min(1,Math.max(0,(now-started)/duration));
  const strength=p<.32?(p/.32):(1-(p-.32)/.68);
  const scale=1+.022*Math.max(0,strength);
  frame.style.setProperty('transform','scale('+scale.toFixed(4)+')','important');
  frame.style.setProperty('opacity',(0.68+0.32*strength).toFixed(3),'important');
  frame.style.setProperty('border-color',strength>.18?'rgba(255,224,142,.98)':'rgba(237,195,77,.72)','important');
  frame.style.setProperty('box-shadow',strength>.12?peakShadow:baseShadow,'important');
  if(p<1)frame.__rimaPulseRAF=requestAnimationFrame(draw);
  else{
   frame.__rimaPulseRAF=0;
   frame.style.setProperty('transform','scale(1)','important');
   frame.style.setProperty('opacity','.68','important');
   frame.style.setProperty('border-color','rgba(237,195,77,.72)','important');
   frame.style.setProperty('box-shadow',baseShadow,'important');
  }
 };
 frame.__rimaPulseRAF=requestAnimationFrame(draw);
 window.__rimaFramePulseCount=(window.__rimaFramePulseCount||0)+1;
 window.__rimaFramePulseLastAt=Date.now();
}
"""
pattern=r'function rimaPulseStageFrame\(\)\{[\s\S]*?\n\}'
h,n=re.subn(pattern,frame.rstrip(),h,count=1)
if n!=1:
 raise SystemExit('V27_FAIL: não encontrei a função da moldura existente')

# Garantir que a chamada de pulso permanece dentro do pulso musical, nunca no observer das palavras.
m=re.search(r'function pulse\(q\)\{[\s\S]*?\n\}',h)
if not m:
 raise SystemExit('V27_FAIL: função pulse(q) não encontrada')
block=m.group(0)
if 'rimaPulseStageFrame();' not in block:
 block=block[:-1]+'\n rimaPulseStageFrame();\n}'
 h=h[:m.start()]+block+h[m.end():]

css=r"""<style id="rimalab-frame-impact-v27">
/* A moldura é uma camada independente; texto e layout nunca recebem transform. */
#lv:not([hidden]) #stg.stage{
 position:relative!important;
 box-sizing:border-box!important;
}
#lv:not([hidden]) #stg.stage::before,
#lv:not([hidden]) #stg.stage::after{
 content:none!important;
 display:none!important;
 animation:none!important;
 transform:none!important;
}
#lv:not([hidden]) #stg.stage > .rima-beat-frame{
 position:absolute!important;
 inset:4px!important;
 z-index:10!important;
 display:block!important;
 box-sizing:border-box!important;
 width:auto!important;
 height:auto!important;
 margin:0!important;
 padding:0!important;
 border:1.5px solid rgba(237,195,77,.72)!important;
 border-radius:17px!important;
 opacity:.68!important;
 pointer-events:none!important;
 transform:scale(1)!important;
 transform-origin:center center!important;
 box-shadow:0 0 12px rgba(237,195,77,.22),inset 0 0 9px rgba(237,195,77,.08)!important;
 will-change:transform,opacity,box-shadow,border-color!important;
}
#lv:not([hidden]) #stg.stage > :not(.rima-beat-frame){
 position:relative!important;
 z-index:1!important;
}
#lv:not([hidden]) #stg.stage #cb,
#lv:not([hidden]) #stg.stage #cb *,
#lv:not([hidden]) #stg.stage #cb.beat-word-hit{
 animation:none!important;
 transform:none!important;
 transition:none!important;
}
</style>"""
if 'id="rimalab-frame-impact-v27"' not in h:
 pos=h.lower().rfind('</body>')
 if pos<0: raise SystemExit('V27_FAIL: </body> não encontrado')
 h=h[:pos]+css+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+46\b',g):
 g=re.sub(r'\bversionCode\s+46\b','versionCode 47',g,count=1)
elif not re.search(r'\bversionCode\s+47\b',g):
 raise SystemExit('V27_FAIL: versionCode inesperado')
if "versionName '3.0.4'" in g:
 g=g.replace("versionName '3.0.4'","versionName '3.0.5'",1)
elif "versionName '3.0.5'" not in g:
 raise SystemExit('V27_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('V27_OK: moldura independente, pulso real de 2,2% acionado somente pelo beat; palavra e layout sem escala')