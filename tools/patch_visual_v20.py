#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
h=hp.read_text(encoding='utf-8')

# v20 abandons CSS keyframes/transitions for the beat pulse. Older stylesheets
# contain global reduced-motion and legacy pseudo-element rules; animate the
# dedicated border node with per-frame inline !important values instead.
pattern=r'function rimaPulseStageFrame\(\)\{[\s\S]*?\n\}\nfunction pulse\(q\)\{'
m=re.search(pattern,h)
if not m:
    raise SystemExit('V20_FAIL: rimaPulseStageFrame()/pulse() não encontrados')
new=r"""function rimaPulseStageFrame(){
 const stage=$('#stg');
 const screen=$('#lv');
 if(!stage||!screen||screen.hidden)return;
 let frame=stage.querySelector('.rima-beat-frame');
 if(!frame){
  frame=document.createElement('span');
  frame.className='rima-beat-frame';
  frame.setAttribute('aria-hidden','true');
  frame.style.setProperty('position','absolute','important');
  frame.style.setProperty('inset','5px','important');
  frame.style.setProperty('z-index','0','important');
  frame.style.setProperty('display','block','important');
  frame.style.setProperty('box-sizing','border-box','important');
  frame.style.setProperty('border','1.5px solid rgba(237,195,77,.42)','important');
  frame.style.setProperty('border-radius','17px','important');
  frame.style.setProperty('pointer-events','none','important');
  frame.style.setProperty('transform-origin','center center','important');
  stage.insertBefore(frame,stage.firstChild);
 }
 if(frame.__rimaPulseRAF)cancelAnimationFrame(frame.__rimaPulseRAF);
 const started=performance.now();
 const duration=240;
 const baseShadow='0 0 9px rgba(237,195,77,.10), inset 0 0 8px rgba(237,195,77,.035)';
 const peakShadow='0 0 24px rgba(237,195,77,.34), 0 0 38px rgba(237,195,77,.17), inset 0 0 14px rgba(237,195,77,.07)';
 const draw=now=>{
  const p=Math.min(1,Math.max(0,(now-started)/duration));
  const scale=p<.34?1+.035*(p/.34):1+.035*(1-(p-.34)/.66);
  const strength=p<.34?p/.34:1-(p-.34)/.66;
  const opacity=.5+.5*strength;
  frame.style.setProperty('transform','scale('+scale.toFixed(4)+')','important');
  frame.style.setProperty('opacity',opacity.toFixed(3),'important');
  frame.style.setProperty('border-color',p>.18&&p<.72?'rgba(255,224,142,.98)':'rgba(237,195,77,.42)','important');
  frame.style.setProperty('box-shadow',strength>.12?peakShadow:baseShadow,'important');
  if(p<1){frame.__rimaPulseRAF=requestAnimationFrame(draw)}
  else{
   frame.__rimaPulseRAF=0;
   frame.style.setProperty('transform','scale(1)','important');
   frame.style.setProperty('opacity','.5','important');
   frame.style.setProperty('border-color','rgba(237,195,77,.42)','important');
   frame.style.setProperty('box-shadow',baseShadow,'important');
  }
 };
 frame.__rimaPulseRAF=requestAnimationFrame(draw);
 window.__rimaBeatPulseCount=(window.__rimaBeatPulseCount||0)+1;
 window.__rimaBeatPulseLastAt=Date.now();
}
function pulse(q){"""
h=h[:m.start()]+new+h[m.end():]

# Remove reliance on CSS keyframes for this layer. The fixed stage and the
# frame's base geometry remain; JavaScript owns the only animated properties.
h=re.sub(r'<style id="rimalab-visual-v19">[\s\S]*?</style>','',h)
css=r"""<style id="rimalab-visual-v20">
#lv:not([hidden]) #stg.stage{
 box-sizing:border-box!important;width:100%!important;height:450px!important;
 min-height:450px!important;max-height:450px!important;flex:0 0 450px!important;
 min-width:0!important;position:relative!important;display:flex!important;
 flex-direction:column!important;align-items:stretch!important;justify-content:space-evenly!important;
 gap:5px!important;overflow:hidden!important;isolation:isolate!important;
 transform:none!important;transition:none!important;animation:none!important;
}
#lv:not([hidden]) #stg.stage > :not(.rima-beat-frame){position:relative!important;z-index:1!important;flex:0 0 auto!important;min-width:0!important}
#lv:not([hidden]) #stg.stage #ck{margin:4px 0 0!important;line-height:1.25!important}
#lv:not([hidden]) #stg.stage #cb{
 margin:4px 0 8px!important;padding:4px 8px!important;line-height:1.04!important;
 letter-spacing:.015em!important;font-kerning:normal!important;transform:none!important;
 animation:none!important;filter:none!important;transition:none!important;
 text-shadow:0 0 4px rgba(237,195,77,.10)!important;
}
#lv:not([hidden]) #stg.stage #cs{margin:4px 0!important;line-height:1.35!important}
#lv:not([hidden]) #stg.stage #rm{margin:4px 0!important;display:flex!important;flex-wrap:wrap!important;justify-content:center!important;gap:8px!important}
#lv:not([hidden]) #stg.stage #sg{margin:6px 0!important;min-height:10px!important}
#lv:not([hidden]) #stg.stage #cn{margin:4px 0 6px!important;line-height:1.3!important}
#lv:not([hidden]) #stg.stage .v3bar{position:relative!important;z-index:1!important;margin:4px auto 2px!important;flex:0 0 auto!important}
#lv:not([hidden]) #stg.stage > .rima-beat-frame{
 position:absolute!important;inset:5px!important;z-index:0!important;display:block!important;
 box-sizing:border-box!important;border:1.5px solid rgba(237,195,77,.42)!important;
 border-radius:17px!important;opacity:.5!important;pointer-events:none!important;
 transform:scale(1)!important;transform-origin:center center!important;
 box-shadow:0 0 9px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important;
 will-change:transform,opacity,box-shadow,border-color!important;
}
#lv:not([hidden]) #stg.stage #cb,#lv:not([hidden]) #stg.stage #cb.beat-word-hit{
 transform:none!important;animation:none!important;filter:none!important;transition:none!important;
}
.rima-select-beat-note{margin:8px 0!important;padding:10px 12px!important;border:1px solid rgba(237,195,77,.7)!important;border-radius:10px!important;background:rgba(237,195,77,.10)!important;color:#ffe4a0!important;font-weight:700!important;text-align:center!important}
#train-step-2 #bp.rima-select-focus{outline:2px solid rgba(237,195,77,.75)!important;outline-offset:5px!important;border-radius:12px!important}
</style>"""
if 'id="rimalab-visual-v20"' not in h:
    pos=h.lower().rfind('</body>')
    if pos<0:raise SystemExit('V20_FAIL: </body> não encontrado')
    h=h[:pos]+css+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')

gp=root/'app/build.gradle'
g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+39\b',g):g=re.sub(r'\bversionCode\s+39\b','versionCode 40',g,count=1)
elif not re.search(r'\bversionCode\s+40\b',g):raise SystemExit('V20_FAIL: versionCode inesperado')
if "versionName '2.9.12'" in g:g=g.replace("versionName '2.9.12'","versionName '2.9.13'",1)
elif "versionName '2.9.13'" not in g:raise SystemExit('V20_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V20_OK: pulso quadro a quadro via JS/inline !important; CSS keyframes removidos; palco fixo e texto imóvel')
