#!/usr/bin/env python3
from pathlib import Path
import re,sys

root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

# 1) Use a dedicated, absolutely-positioned frame layer. Never toggle .hit on the
# stage itself because legacy .stage.hit .word rules animate/scale the text.
pulse_at=h.find('function pulse(q){')
start_at=h.find('function start(){',pulse_at)
if pulse_at<0 or start_at<0:
    raise SystemExit('V19_FAIL: pulse()/start() não encontrados')
pulse_block=r"""function rimaPulseStageFrame(){
 const stage=$('#stg');
 if(!stage||$('#lv').hidden)return;
 let frame=stage.querySelector('.rima-beat-frame');
 if(!frame){
  frame=document.createElement('span');
  frame.className='rima-beat-frame';
  frame.setAttribute('aria-hidden','true');
  stage.insertBefore(frame,stage.firstChild);
 }
 frame.classList.remove('is-pulsing');
 void frame.offsetWidth;
 frame.classList.add('is-pulsing');
 clearTimeout(frame.__rimaPulseTimer);
 frame.__rimaPulseTimer=setTimeout(()=>frame.classList.remove('is-pulsing'),480);
 window.__rimaBeatPulseCount=(window.__rimaBeatPulseCount||0)+1;
}
function pulse(q){
 if(CNT&&q>0){
  const e=$('#lv').hidden?($('#sb')||(B&&B.cin?$('#cd'):null)):$('#cb');
  if(e){e.textContent=4-q;e.style.fontSize='96px';e.style.transform='none';e.style.animation='none'}
 }
 $$('.dots').forEach(c=>[...c.children].forEach((d,j)=>d.classList.toggle('on',j==q)));
 rimaPulseStageFrame();
}
"""
h=h[:pulse_at]+pulse_block+h[start_at:]

# 2) Replace lvStart as a single, ordered transition. Keep step 2 visible on a
# missing selection, and apply immersive positioning before revealing #lv.
lv_at=h.find('function lvStart(){')
stop_at=h.find('function lvStop(){',lv_at)
if lv_at<0 or stop_at<0:
    raise SystemExit('V19_FAIL: lvStart()/lvStop() não encontrados')
lv_start=r"""function lvStart(){
 if(window.__RIMA_LV_START_LOCK)return;
 const selected=ZS.k==='syn'||(ZS.k==='lib'&&!!ZS.key&&Array.isArray(ZLIB[ZS.s])&&ZLIB[ZS.s][1].some(x=>zKey(x)===ZS.key));
 if(!selected){
  const bp=$('#bp');
  let note=$('#rima-select-beat-note');
  if(!note&&bp){
   note=document.createElement('p');
   note.id='rima-select-beat-note';
   note.className='rima-select-beat-note';
   bp.parentNode.insertBefore(note,bp);
  }
  if(note)note.textContent='Selecione um beat antes de começar o treino.';
  if(bp){
   bp.classList.add('rima-select-focus');
   bp.scrollIntoView({behavior:'smooth',block:'center'});
   setTimeout(()=>bp.classList.remove('rima-select-focus'),1500);
  }
  return;
 }
 const oldNote=$('#rima-select-beat-note');if(oldNote)oldNote.remove();
 window.__RIMA_LV_START_LOCK=true;
 ZNR=1;unlock();NA=null;SAID=-9;CNT=0;t0=Date.now();
 const screen=$('#lv');
 const preview=play&&document.body.classList.contains('pv')&&ZS.k==='lib';
 if(!preview&&play)stop();
 /* Put the screen in its final fixed/immersive layout before making it visible. */
 document.body.classList.add('pl');
 document.body.classList.remove('pv');
 $('#sg').innerHTML='';
 $('#cn').textContent='';
 $('#ck').textContent='Prepare-se';
 $('#cb').textContent='...';
 $('#cb').style.fontSize='56px';
 $('#cs').textContent=mode=='atq'?'Escute o beat.':'Preparando o beat e o palco...';
 screen.style.display='';
 screen.hidden=false;
 wInit();
 if(preview){
  document.body.classList.remove('pv');
  try{if(zA)zA.currentTime=0;else if(ZY.p){ZY.p.seekTo(0);ZY.win=[];if(!ZY.ps)ZY.p.play()}}catch(e){}
  zGridReset();zL=0;zBI=-1;zQ=-1;zPre=-1;ZY.win=[];zMedia();pk();
  window.__RIMA_LV_START_LOCK=false;
  return;
 }
 requestAnimationFrame(()=>requestAnimationFrame(()=>{
  if(screen.hidden){window.__RIMA_LV_START_LOCK=false;return}
  try{start();pk()}
  catch(e){
   try{zFallback('Houve uma falha ao abrir o beat.')}
   catch(_){
    $('#ck').textContent='Não foi possível iniciar';
    $('#cb').textContent='Tente novamente';
    $('#cs').textContent='Volte, escolha outro beat e tente iniciar novamente.'
   }
   window.__RIMA_LV_START_LOCK=false;return
  }
  setTimeout(()=>{window.__RIMA_LV_START_LOCK=false},650)
 }))
}
"""
h=h[:lv_at]+lv_start+h[stop_at:]

# Clear the inline selection warning as soon as a real library beat is selected.
old='ZS.key=zKey(x);ZS.name=x[1];'
new="ZS.key=zKey(x);const __rimaSelectNote=document.getElementById('rima-select-beat-note');if(__rimaSelectNote)__rimaSelectNote.remove();ZS.name=x[1];"
if old in h:
    h=h.replace(old,new,1)
elif 'const __rimaSelectNote=document.getElementById' not in h:
    raise SystemExit('V19_FAIL: ponto de seleção zLP não encontrado')

# Replace the entire v18 stage override (including its 360px fixed height).
h=re.sub(r'<style id="rimalab-visual-v18">.*?</style>','',h,flags=re.S)
css=r"""<style id="rimalab-visual-v19">
/* Fixed stage geometry: enough room for title, word, rhyme samples, progress and hint. */
#lv:not([hidden]) #stg.stage{
 box-sizing:border-box!important;
 width:100%!important;
 height:450px!important;
 min-height:450px!important;
 max-height:450px!important;
 flex:0 0 450px!important;
 min-width:0!important;
 position:relative!important;
 display:flex!important;
 flex-direction:column!important;
 align-items:stretch!important;
 justify-content:space-evenly!important;
 gap:5px!important;
 overflow:hidden!important;
 isolation:isolate!important;
 transform:none!important;
 transition:none!important;
 animation:none!important;
}
#lv:not([hidden]) #stg.stage > :not(.rima-beat-frame){
 position:relative!important;
 z-index:1!important;
 flex:0 0 auto!important;
 min-width:0!important;
}
#lv:not([hidden]) #stg.stage #ck{margin:4px 0 0!important;line-height:1.25!important}
#lv:not([hidden]) #stg.stage #cb{
 margin:4px 0 8px!important;
 padding:4px 8px!important;
 line-height:1.04!important;
 letter-spacing:.015em!important;
 font-kerning:normal!important;
 transform:none!important;
 animation:none!important;
 filter:none!important;
 transition:none!important;
 text-shadow:0 0 4px rgba(237,195,77,.10)!important;
}
#lv:not([hidden]) #stg.stage #cs{margin:4px 0!important;line-height:1.35!important}
#lv:not([hidden]) #stg.stage #rm{margin:4px 0!important;display:flex!important;flex-wrap:wrap!important;justify-content:center!important;gap:8px!important}
#lv:not([hidden]) #stg.stage #sg{margin:6px 0!important;min-height:10px!important}
#lv:not([hidden]) #stg.stage #cn{margin:4px 0 6px!important;line-height:1.3!important}
#lv:not([hidden]) #stg.stage .v3bar{position:relative!important;z-index:1!important;margin:4px auto 2px!important;flex:0 0 auto!important}
/* Dedicated border layer: only this element scales; parent and all content stay still. */
#lv:not([hidden]) #stg.stage > .rima-beat-frame{
 position:absolute!important;
 inset:5px!important;
 z-index:0!important;
 display:block!important;
 box-sizing:border-box!important;
 border:1.5px solid rgba(237,195,77,.42)!important;
 border-radius:17px!important;
 opacity:.5!important;
 pointer-events:none!important;
 transform:scale(1)!important;
 transform-origin:center center!important;
 box-shadow:0 0 9px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important;
}
#lv:not([hidden]) #stg.stage > .rima-beat-frame.is-pulsing{
 animation:rimalab-frame-impact-v19 .46s cubic-bezier(.2,.75,.25,1) both!important;
}
@keyframes rimalab-frame-impact-v19{
 0%{opacity:.5;transform:scale(1);border-color:rgba(237,195,77,.42)!important;box-shadow:0 0 9px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important}
 38%{opacity:1;transform:scale(1.035);border-color:rgba(255,224,142,.98)!important;box-shadow:0 0 24px rgba(237,195,77,.34),0 0 38px rgba(237,195,77,.17),inset 0 0 14px rgba(237,195,77,.07)!important}
 100%{opacity:.5;transform:scale(1);border-color:rgba(237,195,77,.42)!important;box-shadow:0 0 9px rgba(237,195,77,.10),inset 0 0 8px rgba(237,195,77,.035)!important}
}
/* No legacy .hit class on #stg; the main word never participates in the animation. */
#lv:not([hidden]) #stg.stage #cb,
#lv:not([hidden]) #stg.stage #cb.beat-word-hit{
 transform:none!important;
 animation:none!important;
 filter:none!important;
 transition:none!important;
}
.rima-select-beat-note{
 margin:8px 0!important;
 padding:10px 12px!important;
 border:1px solid rgba(237,195,77,.7)!important;
 border-radius:10px!important;
 background:rgba(237,195,77,.10)!important;
 color:#ffe4a0!important;
 font-weight:700!important;
 text-align:center!important;
}
#train-step-2 #bp.rima-select-focus{outline:2px solid rgba(237,195,77,.75)!important;outline-offset:5px!important;border-radius:12px!important}
</style>"""
if 'id="rimalab-visual-v19"' not in h:
    pos=h.lower().rfind('</body>')
    if pos<0:raise SystemExit('V19_FAIL: </body> não encontrado')
    h=h[:pos]+css+'\n'+h[pos:]
hp.write_text(h,encoding='utf-8')

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+38\b',g):g=re.sub(r'\bversionCode\s+38\b','versionCode 39',g,count=1)
elif not re.search(r'\bversionCode\s+39\b',g):raise SystemExit('V19_FAIL: versionCode inesperado')
if "versionName '2.9.11'" in g:g=g.replace("versionName '2.9.11'","versionName '2.9.12'",1)
elif "versionName '2.9.12'" not in g:raise SystemExit('V19_FAIL: versionName inesperado')
gp.write_text(g,encoding='utf-8')
print('VISUAL_V19_OK: palco 450px fixo, frame independente pulsa no zTick, texto estático, guard sem reset, transição sem flash')
