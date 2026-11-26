#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# Keep the existing v20 frame animator and audio-clock callback; add only a
# restrained, non-transforming highlight to the word on the same pulse.
if 'function rimaPulseStageWord()' not in h:
    pulse_fn=r"""function rimaPulseStageWord(){
 const word=$('#cb'),screen=$('#lv');
 if(!word||!screen||screen.hidden)return;
 if(word.__rimaWordRAF)cancelAnimationFrame(word.__rimaWordRAF);
 const started=performance.now(),duration=190;
 const baseShadow='0 0 4px rgba(237,195,77,.10)';
 const peakShadow='0 0 8px rgba(255,231,174,.48),0 0 19px rgba(237,195,77,.28),0 0 30px rgba(237,195,77,.12)';
 const draw=now=>{
  const p=Math.min(1,Math.max(0,(now-started)/duration));
  const strength=p<.22?p/.22:1-(p-.22)/.78;
  const brightness=1+(0.12*strength);
  word.style.setProperty('color',strength>.12?'#ffe8ad':'#edc34d','important');
  word.style.setProperty('text-shadow',strength>.12?peakShadow:baseShadow,'important');
  word.style.setProperty('filter','brightness('+brightness.toFixed(3)+')','important');
  word.style.setProperty('transform','none','important');
  if(p<1)word.__rimaWordRAF=requestAnimationFrame(draw);
  else{
   word.__rimaWordRAF=0;
   word.style.setProperty('color','#edc34d','important');
   word.style.setProperty('text-shadow',baseShadow,'important');
   word.style.setProperty('filter','none','important');
   word.style.setProperty('transform','none','important');
  }
 };
 word.__rimaWordRAF=requestAnimationFrame(draw);
 window.__rimaWordPulseCount=(window.__rimaWordPulseCount||0)+1;
}
"""
    idx=h.find('function pulse(q){')
    if idx<0: raise SystemExit('V21_FAIL: pulse(q) não encontrado')
    h=h[:idx]+pulse_fn+h[idx:]

m=re.search(r'function pulse\(q\)\{[^\n]*\}',h)
if not m: raise SystemExit('V21_FAIL: bloco pulse(q) não encontrado')
block=m.group(0)
if 'rimaPulseStageWord();' not in block:
    if 'rimaPulseStageFrame();' not in block: raise SystemExit('V21_FAIL: chamada da moldura não encontrada em pulse(q)')
    block=block.replace('rimaPulseStageFrame();','rimaPulseStageFrame();rimaPulseStageWord();',1)
    h=h[:m.start()]+block+h[m.end():]

h=re.sub(r'<style id="rimalab-visual-v20">[\s\S]*?</style>','',h)
css=r"""<style id="rimalab-visual-v21">
#lv:not([hidden]) #stg.stage{
 box-sizing:border-box!important;width:100%!important;height:450px!important;
 min-height:450px!important;max-height:450px!important;flex:0 0 450px!important;
 min-width:0!important;position:relative!important;display:flex!important;
 flex-direction:column!important;align-items:stretch!important;justify-content:space-between!important;
 gap:0!important;padding:13px 14px 18px!important;
 overflow:hidden!important;isolation:isolate!important;
 transform:none!important;transition:none!important;animation:none!important;
}
#lv:not([hidden]) #stg.stage > :not(.rima-beat-frame){
 position:relative!important;z-index:1!important;flex:0 0 auto!important;min-width:0!important;
}
#lv:not([hidden]) #stg.stage #ck{margin:0!important;padding:0!important;line-height:1.2!important}
#lv:not([hidden]) #stg.stage #cb{
 margin:0!important;padding:0 8px!important;line-height:1.02!important;
 letter-spacing:.015em!important;font-kerning:normal!important;transform:none!important;
 animation:none!important;filter:none!important;transition:none!important;
 text-shadow:0 0 4px rgba(237,195,77,.10)!important;
}
#lv:not([hidden]) #stg.stage #cs{margin:0!important;padding:0 2px!important;line-height:1.28!important}
#lv:not([hidden]) #stg.stage #rm{
 margin:0!important;padding:0 2px!important;display:flex!important;flex-wrap:wrap!important;
 justify-content:center!important;gap:8px!important;min-height:0!important;
}
#lv:not([hidden]) #stg.stage #sg{margin:0!important;padding:0!important;min-height:8px!important}
#lv:not([hidden]) #stg.stage #cn{margin:0!important;padding:0!important;line-height:1.22!important}
#lv:not([hidden]) #stg.stage .v3bar{
 position:relative!important;z-index:1!important;box-sizing:border-box!important;
 width:100%!important;display:flex!important;justify-content:center!important;
 margin:2px auto 0!important;padding:0 0 7px!important;flex:0 0 auto!important;
}
#lv:not([hidden]) #stg.stage .v3bar button{
 box-sizing:border-box!important;max-width:100%!important;margin:0!important;
}
#lv:not([hidden]) #stg.stage > .rima-beat-frame{
 position:absolute!important;inset:5px!important;z-index:0!important;display:block!important;
 box-sizing:border-box!important;border:1.5px solid rgba(237,195,77,.42)!important;
 border-radius:17px!important;opacity:.5!important;pointer-events:none!important;
 transform:scale(1)!important;transform-origin:center center!important;
 box-shadow:0 0 10px rgba(237,195,77,.12),inset 0 0 10px rgba(237,195,77,.045)!important;
 will-change:transform,opacity,box-shadow,border-color!important;
}
#lv:not([hidden]) #stg.stage #cb,
#lv:not([hidden]) #stg.stage #cb.beat-word-hit{
 transform:none!important;animation:none!important;transition:none!important;
}
</style>"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V21_FAIL: </body> não encontrado')
h=h[:pos]+css+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+40\b',g):g=re.sub(r'\bversionCode\s+40\b','versionCode 41',g,count=1)
elif not re.search(r'\bversionCode\s+41\b',g):raise SystemExit('V21_FAIL: versionCode inesperado')
if "versionName '2.9.13'" in g:g=g.replace("versionName '2.9.13'","versionName '2.9.14'",1)
elif "versionName '2.9.14'" not in g:raise SystemExit('V21_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V21_OK: dica com área inferior reservada; palavra recebe brilho sutil sincronizado sem movimento; palco fixo')
