#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V68_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8');g=gp.read_text(encoding='utf-8')
if 'rimalab-audio-retry-lifecycle-v68' in h: raise SystemExit('V68_FAIL: patch já aplicado')
# A failed audio request stops playback. Mark recovery in BOTH setup and live
# stage branches, and replace the stale "opening" status with a real failure.
old=""" stop();
 if(inLiveStage){"""
new=""" stop();
 window.__rimaV58RecoveryPending=true;
 if(inLiveStage){"""
if h.count(old)!=1: raise SystemExit('V68_FAIL: zFallback stop branch not found uniquely')
h=h.replace(old,new,1)
old="""  window.__rimaV58RecoveryPending=true;
  return;
 }
 if(setup&&!setup.hidden){
  const bp=document.getElementById('bp');"""
new="""  return;
 }
 if(setup&&!setup.hidden){
  const cs=document.getElementById('cs');if(cs)cs.textContent='Esse beat não abriu. Escolha outra faixa.';
  const bp=document.getElementById('bp');"""
if h.count(old)!=1: raise SystemExit('V68_FAIL: setup fallback branch not found uniquely')
h=h.replace(old,new,1)
# Replace the recovery handler in the actual V58 wrapper. In setup, restart
# the preview player; in the live stage, restart the stage itself.
old="""   const pending=!!window.__rimaV58RecoveryPending;
   if(pending&&window.ZS&&ZS.k==='lib'&&ZS.key&&document.getElementById('lv')&&!document.getElementById('lv').hidden){
    window.__rimaV58RecoveryPending=false;
    const note=document.querySelector('.rima-v58-audio-error');if(note)note.remove();
    requestAnimationFrame(()=>{if(typeof window.lvStart==='function')window.lvStart()});
   }"""
new="""   const pending=!!window.__rimaV58RecoveryPending;
   if(pending&&window.ZS&&ZS.k==='lib'&&ZS.key){
    window.__rimaV58RecoveryPending=false;
    const note=document.querySelector('.rima-v58-audio-error');if(note)note.remove();
    const lv=document.getElementById('lv'),setup=document.getElementById('train-step-2');
    const live=!!(lv&&!lv.hidden),inSetup=!!(setup&&!setup.hidden);
    const cs=document.getElementById('cs');if(cs)cs.textContent=live?'Preparando o beat e o palco...':'';
    requestAnimationFrame(()=>{
     if(live&&typeof window.lvStart==='function')window.lvStart();
     else if(inSetup&&typeof window.start==='function')window.start();
     else if(inSetup&&typeof window.zLoad==='function'){window.play=true;window.zLoad(0)}
    });
   }"""
if h.count(old)!=1: raise SystemExit('V68_FAIL: V58 recovery handler not found uniquely')
h=h.replace(old,new,1)
# Reduce the gap from 22px to 12px without collapsing the two rows.
h=h.replace("categoryRow.style.setProperty('margin-bottom','22px','important')","categoryRow.style.setProperty('margin-bottom','12px','important')",1)
h=h.replace("bar.style.setProperty('margin-bottom','14px','important')","bar.style.setProperty('margin-bottom','10px','important')",1)
css=r'''<style id="rimalab-audio-retry-lifecycle-v68">
/* Keep a clear but tighter separation between category chips and Favorites. */
#lv:not([hidden]) #bq>.rima-v50-category-row{
 margin-bottom:12px!important;padding-bottom:3px!important
}
#lv:not([hidden]) #bq>.rima-v43-tools{margin-top:0!important;margin-bottom:10px!important}
/* Do not let a stale loading label survive an audio failure/retry. */
.rima-v58-audio-error{display:block!important}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V68_FAIL: body ausente')
h=h[:pos]+css+'\n'+h[pos:]
m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='87': raise SystemExit('V68_FAIL: versionCode base não é 87')
g=g[:m.start(1)]+'88'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.5': raise SystemExit('V68_FAIL: versionName base não é 3.4.5')
g=g[:m.start(1)]+'3.4.6'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V68_OK: failed audio releases pending state; next selection restarts preview/stage; stale loading status cleared; selector gap reduced; 3.4.6/code88')
