#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=next((p for p in (root/'app/build.gradle',root/'app/build.gradle.kts') if p.exists()),None)
if not hp.is_file() or gp is None: raise SystemExit('V64_FAIL: HTML/Gradle ausente')
h=hp.read_text(encoding='utf-8'); g=gp.read_text(encoding='utf-8')
if 'rimalab-stage-selector-gap-entry-message-v64' in h: raise SystemExit('V64_FAIL: patch já aplicado')
if 'rimalab-favorites-player-scroll-stage-v62' not in h or 'rimalab-favorites-selection-colors-v63' not in h:
 raise SystemExit('V64_FAIL: base V62/V63 ausente')

css=r'''<style id="rimalab-stage-selector-gap-entry-message-v64">
/* Live stage: keep category chips and Favorites on separate, fully visible rows. */
#lv #bq .rima-v50-category-row,
#lv #bp .rima-v50-category-row,
#lv #bbq .rima-v50-category-row{
 display:flex!important;flex-flow:row wrap!important;align-items:center!important;
 gap:9px!important;box-sizing:border-box!important;
 min-height:48px!important;height:auto!important;
 margin:0 0 14px!important;padding:2px 0 5px!important;
 overflow:visible!important;position:relative!important;
}
#lv #bq .rima-v50-category-row>.tag.chip,
#lv #bp .rima-v50-category-row>.tag.chip,
#lv #bbq .rima-v50-category-row>.tag.chip{
 box-sizing:border-box!important;flex:1 1 0!important;min-width:0!important;
 min-height:42px!important;height:auto!important;margin:0!important;
 overflow:visible!important;position:relative!important;
}
#lv #bq>.rima-v43-tools,
#lv #bp>.rima-v43-tools,
#lv #bbq>.rima-v43-tools{
 display:block!important;box-sizing:border-box!important;
 position:relative!important;clear:both!important;
 width:100%!important;max-width:100%!important;
 height:auto!important;min-height:0!important;
 margin:8px 0 12px!important;padding:0!important;
 overflow:visible!important;
}
#lv #bq>.rima-v43-tools .rima-v43-toggle,
#lv #bp>.rima-v43-tools .rima-v43-toggle,
#lv #bbq>.rima-v43-tools .rima-v43-toggle{
 box-sizing:border-box!important;width:100%!important;max-width:100%!important;
 min-height:46px!important;height:auto!important;margin:0!important;
}
@media(orientation:landscape){
 #lv #bq .rima-v50-category-row,
 #lv #bp .rima-v50-category-row,
 #lv #bbq .rima-v50-category-row{gap:7px!important;margin-bottom:12px!important}
 #lv #bq .rima-v50-category-row>.tag.chip,
 #lv #bp .rima-v50-category-row>.tag.chip,
 #lv #bbq .rima-v50-category-row>.tag.chip{min-height:38px!important}
}
</style>'''
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V64_FAIL: </body> ausente')
h=h[:pos]+css+'\n'+h[pos:]

runtime=r'''<script id="rimalab-stage-selector-gap-entry-message-runtime-v64">
(function(){
 'use strict';
 function publishEntryMessage(){
  try{
   const line=document.getElementById('cs');
   if(!line)return;
   const state=typeof ZS!=='undefined'&&ZS?ZS:null;
   if(!state)return;
   const message=state.k==='syn'?'':(state.auto?'Beat sem introdução: já começa com tudo.':'Virada detectada. Entrando um pouco antes dela.');
   if(message&&line.textContent.trim()!==message)line.textContent=message;
  }catch(_){}
 }
 function scheduleEntryMessage(){
  publishEntryMessage();
  requestAnimationFrame(publishEntryMessage);
  setTimeout(publishEntryMessage,80);
  setTimeout(publishEntryMessage,240);
  setTimeout(publishEntryMessage,520);
 }
 function wrap(name){
  const old=window[name];
  if(typeof old!=='function'||old.__rimaV64)return;
  const wrapped=function(){
   const result=old.apply(this,arguments);
   scheduleEntryMessage();
   return result;
  };
  wrapped.__rimaV64=true;window[name]=wrapped;
 }
 wrap('wStart');
 wrap('lvStart');
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)scheduleEntryMessage()});
 window.addEventListener('orientationchange',()=>setTimeout(scheduleEntryMessage,100),{passive:true});
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scheduleEntryMessage,{once:true});
 else scheduleEntryMessage();
 window.rimaV64RestoreEntryMessage=scheduleEntryMessage;
})();</script>'''
pos=h.lower().rfind('</body>')
h=h[:pos]+runtime+'\n'+h[pos:]

m=re.search(r'\bversionCode\s*(?:=\s*)?(\d+)',g)
if not m or m.group(1)!='83': raise SystemExit('V64_FAIL: versionCode base não é 83')
g=g[:m.start(1)]+'84'+g[m.end(1):]
m=re.search(r'\bversionName\s*(?:=\s*)?["\']([^"\']+)["\']',g)
if not m or m.group(1)!='3.4.1': raise SystemExit('V64_FAIL: versionName base não é 3.4.1')
g=g[:m.start(1)]+'3.4.2'+g[m.end(1):]
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V64_OK: separates live selector rows; restores entry message after stage start; 3.4.2/code84')
