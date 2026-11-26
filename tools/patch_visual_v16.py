#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
h=h.replace('letter-spacing:-.045em!important;','letter-spacing:.015em!important;')
h=h.replace('#stg{display:flex!important;visibility:visible!important;opacity:1!important;min-height:52vh!important;','#stg{display:flex!important;visibility:visible!important;opacity:1!important;min-height:45vh!important;')
h=h.replace('const available=Math.max(120,stage.clientWidth-54);','const available=Math.max(120,stage.clientWidth-64);')
style=r"""<style id="rimalab-visual-v16">
#stg.stage{min-height:45vh!important;position:relative!important;overflow:visible!important;isolation:isolate!important}
#stg.stage #cb{letter-spacing:.015em!important;font-kerning:normal!important;font-stretch:normal!important;text-shadow:0 0 12px rgba(237,195,77,.24),0 0 26px rgba(237,195,77,.12)!important}
#stg.stage.hit{border-color:rgba(255,220,126,.98)!important;box-shadow:0 0 0 1px rgba(237,195,77,.34),0 0 30px rgba(237,195,77,.42),0 0 52px rgba(237,195,77,.18),inset 0 0 28px rgba(237,195,77,.12)!important}
#stg.stage::after{inset:-5px!important;border:1.5px solid rgba(237,195,77,.25)!important;border-radius:inherit!important;opacity:.28!important;box-shadow:0 0 12px rgba(237,195,77,.12),inset 0 0 14px rgba(237,195,77,.06)!important}
#stg.stage.hit::after{animation:rimalab-frame-pulse-v16 .42s cubic-bezier(.2,.8,.2,1)!important}
@keyframes rimalab-frame-pulse-v16{0%{opacity:1;inset:-8px!important;border-color:rgba(255,235,174,1)!important;box-shadow:0 0 34px rgba(237,195,77,.62),0 0 58px rgba(237,195,77,.26),inset 0 0 24px rgba(237,195,77,.2)!important}100%{opacity:.24;inset:-5px!important;border-color:rgba(237,195,77,.25)!important;box-shadow:0 0 10px rgba(237,195,77,.12),inset 0 0 8px rgba(237,195,77,.04)!important}}
#stg.stage #cb.beat-word-hit{letter-spacing:.015em!important;text-shadow:0 0 9px rgba(255,239,195,.95),0 0 24px rgba(237,195,77,.76),0 0 46px rgba(237,195,77,.4)!important}
@media(prefers-reduced-motion:reduce){#stg.stage.hit::after{animation:none!important;opacity:.28!important}}
</style>"""
if 'id="rimalab-visual-v16"' not in h:
    pos=h.lower().rfind('</body>')
    if pos<0: raise SystemExit('V16_FAIL: </body> não encontrado')
    h=h[:pos]+style+'\n'+h[pos:]
old="function zLP(i,auto,style){if(style&&ZLIB[style])ZS.s=style;zSavePos();ZCARRY=null;if(!auto)zTries=0;const x=ZLIB[ZS.s][1][i];ZS.k=ZS.tab='lib';ZS.i=i;ZS.lid=x[0];ZS.src=x[0];ZS.key=zKey(x);ZS.name=x[1];ZS.bpm=ZS.b0=x[2]||ZLIB[ZS.s][0];ZS.off=x[3]||0;ZS.ph=0;ZS.sy=0;ZS.adj=0;try{ZS.adj=+localStorage.getItem('adj_'+ZS.key)||0}catch(e){}zSwap()}"
new="function zLP(i,auto,style){if(style&&ZLIB[style])ZS.s=style;const list=ZLIB[ZS.s]&&ZLIB[ZS.s][1];if(!Array.isArray(list)||!list[i]){try{zBuild(ZS.s)}catch(e){}const retry=ZLIB[ZS.s]&&ZLIB[ZS.s][1];if(!Array.isArray(retry)||!retry[i]){zMsg('Carregando a lista de beats. Toque novamente em instantes.');pk();return}}try{zSavePos()}catch(e){}ZCARRY=null;if(!auto)zTries=0;const x=(ZLIB[ZS.s][1]||[])[i];if(!x)return;ZS.k=ZS.tab='lib';ZS.i=i;ZS.lid=x[0];ZS.src=x[0];ZS.key=zKey(x);ZS.name=x[1];ZS.bpm=ZS.b0=x[2]||ZLIB[ZS.s][0];ZS.off=x[3]||0;ZS.ph=0;ZS.sy=0;ZS.adj=0;try{ZS.adj=+localStorage.getItem('adj_'+ZS.key)||0}catch(e){}try{zSwap()}catch(e){}pk();requestAnimationFrame(()=>{try{pk()}catch(e){}})}"
if old in h: h=h.replace(old,new,1)
elif 'function zLP(i,auto,style){if(style&&ZLIB[style])ZS.s=style;const list=' not in h:
    raise SystemExit('V16_FAIL: função zLP original não encontrada')
hp.write_text(h,encoding='utf-8')
g=gp.read_text(encoding='utf-8')
if 'versionCode 34' in g: g=g.replace('versionCode 34','versionCode 35',1)
elif 'versionCode 35' not in g: raise SystemExit('V16_FAIL: versionCode inesperado')
if "versionName '2.9.7'" in g: g=g.replace("versionName '2.9.7'","versionName '2.9.8'",1)
elif "versionName '2.9.8'" not in g: raise SystemExit('V16_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V16_OK: tracking legível, moldura menor com pulso externo e seleção inicial robusta')
