#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')
if 'rimalab-runtime-on-demand-mic-calibration-v36' in h:
    raise SystemExit('V36_FAIL: patch já aplicado')

# 1. Player só aparece quando há áudio realmente iniciado; etapa 2 não o revela por si só.
gate=r"""
<style id="rimalab-player-on-demand-v36">
body.pl:not(.sy):not(.rima-player-visible) #pbar{display:none!important}
body.pl.rima-player-visible:not(.sy) #pbar{display:flex!important}
@media(orientation:landscape) and (max-height:900px){
 #pbar{position:fixed!important;top:auto!important;left:10px!important;right:10px!important;
  bottom:calc(4px + env(safe-area-inset-bottom,0px))!important;transform:none!important;
  width:auto!important;max-width:none!important;height:49px!important;min-height:49px!important;
  margin:0!important;z-index:12000!important}
 body.pl main,body.pl #lv:not([hidden]){padding-bottom:72px!important}
 #pbar .pwrow{min-height:40px!important}
}
</style>
"""
pos=h.lower().rfind('</body>')
if pos<0: raise SystemExit('V36_FAIL: </body> ausente')
h=h[:pos]+gate+'\n'+h[pos:]

# 2. Replace the old tone-only calibrator with microphone loopback correlation.
cal=r"""
const calHTML=()=>'<section class="card calibrator-card"><div class="cal-top"><span class="cal-icon" aria-hidden="true">♫</span><div><h2>Calibração Bluetooth</h2><p class="mut">Medição automática com o microfone do aparelho.</p></div></div><div class="cal-help"><p>Conecte a caixa Bluetooth e toque em calibrar. O Rima Lab emite cinco sinais curtos, capta o retorno pelo microfone e calcula a compensação pelo atraso mediano. O áudio não é gravado nem enviado.</p></div><div class="cal-visual" id="cal-visual" aria-live="off"><span></span><b>Sinal emitido</b></div><div class="cal-control"><div class="cal-value"><span class="lat-v">'+LAT+'</span><small>ms</small></div><input type="range" class="lat-s" min="0" max="800" step="5" value="'+LAT+'" oninput="setLat(+this.value)" aria-label="Ajuste manual da sincronização Bluetooth"></div><div class="cal-actions"><button id="cal-start" class="btn w cal-button" onclick="cal()">Calibrar com microfone</button><button id="cal-stop" class="btn g w cal-stop" onclick="calCancel()" hidden>Cancelar teste</button></div><p class="mut cm" role="status" aria-live="polite">Pronto. A calibração só ativa o microfone durante este teste. Ajuste manual permanece disponível.</p></section>';
let CAL_RUN=null;
function calRelease(run){
 if(!run||run.released)return;
 run.released=true;
 if(run.timer)clearTimeout(run.timer);
 (run.timers||[]).forEach(t=>clearTimeout(t));
 if(run.processor){try{run.processor.onaudioprocess=null;run.processor.disconnect()}catch(_){}}
 if(run.source){try{run.source.disconnect()}catch(_){}}
 if(run.mute){try{run.mute.disconnect()}catch(_){}}
 (run.nodes||[]).forEach(n=>{try{n.stop()}catch(_){};try{n.disconnect()}catch(_){}});
 if(run.stream)try{run.stream.getTracks().forEach(t=>t.stop())}catch(_){}
}
function calCancel(){
 const run=CAL_RUN;if(!run)return;
 run.cancelled=true;
 if(run.timer)clearTimeout(run.timer);
 (run.timers||[]).forEach(t=>clearTimeout(t));
 if(run.done)run.done();
 const start=$('#cal-start'),stopBtn=$('#cal-stop');
 if(start){start.disabled=false;start.textContent='Calibrar novamente'}
 if(stopBtn)stopBtn.hidden=true;
 $$('.cm').forEach(e=>e.textContent='Teste cancelado. Nenhuma compensação foi alterada.');
}
function setLat(v){
 v=Math.max(0,Math.min(800,+v||0));LAT=v;LATSET=true;
 try{localStorage.setItem('lat',String(v))}catch(e){}
 $$('.lat-v').forEach(e=>e.textContent=String(v));
 $$('.lat-s').forEach(e=>e.value=String(v));
}
function calChirp(sr){
 const seconds=.135,n=Math.floor(sr*seconds),data=new Float32Array(n);
 let phase=0;
 for(let i=0;i<n;i++){
  const t=i/sr,f=620+(1900-620)*(t/seconds);
  phase+=2*Math.PI*f/sr;
  const edge=Math.min(1,t/.012,(seconds-t)/.014);
  const env=Math.max(0,Math.min(1,edge));
  data[i]=.82*Math.sin(phase)*env;
 }
 return data;
}
function calCorrelation(record,template,expectedIndex,sr,stride,maxMs){
 const td=[];for(let i=0;i<template.length;i+=stride)td.push(template[i]);
 if(!td.length)return null;
 let te=0;for(const x of td)te+=x*x;
 if(te<1e-7)return null;
 const limit=Math.min(Math.floor(maxMs*sr/(1000*stride)),record.length-td.length-expectedIndex);
 if(limit<=0)return null;
 const energy=new Float64Array(record.length+1);
 for(let i=0;i<record.length;i++)energy[i+1]=energy[i]+record[i]*record[i];
 const scoreAt=lag=>{
  const start=expectedIndex+lag;
  if(start<0||start+td.length>=record.length)return -1;
  const ey=energy[start+td.length]-energy[start];
  if(ey<1e-7)return -1;
  let dot=0;
  for(let j=0;j<td.length;j++)dot+=td[j]*record[start+j];
  return Math.abs(dot)/Math.sqrt(te*ey);
 };
 let best=-1,bestLag=0;
 for(let lag=0;lag<=limit;lag+=6){const score=scoreAt(lag);if(score>best){best=score;bestLag=lag}}
 const lo=Math.max(0,bestLag-7),hi=Math.min(limit,bestLag+7);
 for(let lag=lo;lag<=hi;lag++){const score=scoreAt(lag);if(score>best){best=score;bestLag=lag}}
 if(best<.105)return null;
 return {delayMs:bestLag*stride/sr*1000,score:best};
}
async function cal(){
 if(CAL_RUN)return;
 const AC=window.AudioContext||window.webkitAudioContext;
 const run={cancelled:false,timers:[],nodes:[],chunks:[],ctx:null,stream:null,source:null,processor:null,mute:null,timer:null,done:null,released:false};
 CAL_RUN=run;
 const start=$('#cal-start'),stopBtn=$('#cal-stop'),visual=$('#cal-visual');
 const status=t=>$$('.cm').forEach(e=>e.textContent=t);
 if(start){start.disabled=true;start.textContent='Solicitando microfone...'}
 if(stopBtn)stopBtn.hidden=false;
 if(visual)visual.classList.remove('is-active');
 try{
  if(!AC)throw new Error('A saída de áudio não está disponível neste WebView.');
  if(!navigator.mediaDevices||typeof navigator.mediaDevices.getUserMedia!=='function')throw new Error('Este WebView não disponibilizou a captura do microfone.');
  const ctx=run.ctx=new AC({latencyHint:'interactive'});
  await ctx.resume();
  if(run.cancelled)return;
  status('Autorize o microfone. Ele será usado apenas para captar os cinco sinais de teste.');
  const stream=run.stream=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:false,noiseSuppression:false,autoGainControl:false},video:false});
  if(run.cancelled)return;
  const tracks=stream.getAudioTracks(),settings=tracks[0]&&tracks[0].getSettings?tracks[0].getSettings():{};
  const micLatencyMs=Number.isFinite(settings.latency)?Math.max(0,settings.latency*1000):0;
  const sr=ctx.sampleRate,template=calChirp(sr),buffer=ctx.createBuffer(1,template.length,sr);
  buffer.copyToChannel(template,0);
  const source=run.source=ctx.createMediaStreamSource(stream);
  const processor=run.processor=ctx.createScriptProcessor(2048,1,1);
  const mute=run.mute=ctx.createGain();mute.gain.value=0;
  processor.onaudioprocess=e=>{
   if(run.cancelled)return;
   try{
    const input=e.inputBuffer.getChannelData(0),stamp=Number.isFinite(e.playbackTime)?e.playbackTime- e.inputBuffer.duration:ctx.currentTime-e.inputBuffer.duration;
    run.chunks.push({time:stamp,data:new Float32Array(input)});
   }catch(_){}
  };
  source.connect(processor);processor.connect(mute);mute.connect(ctx.destination);
  status('Microfone ativo. Mantenha a caixa conectada e próxima; não fale durante a medição.');
  const count=5,spacing=1.12,first=ctx.currentTime+.85,lastAt=first+(count-1)*spacing;
  const gain=ctx.createGain();gain.gain.value=.88;gain.connect(ctx.destination);
  run.nodes.push(gain);
  const emitted=[];
  for(let i=0;i<count;i++){
   const at=first+i*spacing,node=ctx.createBufferSource();node.buffer=buffer;node.connect(gain);node.start(at);node.stop(at+.16);run.nodes.push(node);emitted.push(at);
   const tid=setTimeout(()=>{if(!run.cancelled&&visual){visual.classList.add('is-active');const off=setTimeout(()=>visual.classList.remove('is-active'),160);run.timers.push(off)}},Math.max(0,(at-ctx.currentTime)*1000));
   run.timers.push(tid);
  }
  const waitMs=Math.max(0,(lastAt+1.05-ctx.currentTime)*1000);
  await new Promise(resolve=>{run.done=resolve;run.timer=setTimeout(resolve,waitMs)});
  if(run.cancelled)return;
  if(run.chunks.length<12)throw new Error('O microfone não entregou amostras suficientes. Verifique a permissão e tente novamente.');
  run.processor.onaudioprocess=null;
  const sr0=sr,startTime=Math.min(...run.chunks.map(c=>c.time)),endTime=Math.max(...run.chunks.map(c=>c.time+c.data.length/sr0));
  const rec=new Float32Array(Math.max(1,Math.ceil((endTime-startTime)*sr0)));
  run.chunks.sort((a,b)=>a.time-b.time).forEach(c=>{const off=Math.max(0,Math.round((c.time-startTime)*sr0));if(off<rec.length)rec.set(c.data.subarray(0,rec.length-off),off)});
  const stride=Math.max(2,Math.round(sr0/12000)),dec=new Float32Array(Math.ceil(rec.length/stride));
  for(let i=0,j=0;i<rec.length;i+=stride,j++)dec[j]=rec[i];
  const results=[];
  for(const at of emitted){
   if(run.cancelled)return;
   const expected=Math.round((at-startTime)*sr0/stride);
   const hit=calCorrelation(dec,template,expected,sr0,stride,850);
   if(hit)results.push(hit);
  }
  if(results.length<3)throw new Error('Não consegui identificar pelo menos três retornos com confiança. Aumente o volume da caixa, aproxime-a do microfone e repita.');
  const values=results.map(x=>x.delayMs).sort((a,b)=>a-b),median=values[Math.floor(values.length/2)];
  const spread=values[values.length-1]-values[0];
  if(spread>180)throw new Error('A medição variou demais entre os sinais. Reduza ruído ambiente, aproxime a caixa e repita.');
  const measured=Math.max(0,median-micLatencyMs),applied=Math.max(0,Math.min(800,Math.round(measured/5)*5));
  setLat(applied);
  const quality=results.reduce((a,b)=>a+b.score,0)/results.length;
  status('Atraso acústico estimado: '+Math.round(median)+' ms. Compensação aplicada: '+applied+' ms ('+results.length+'/5 sinais; confiança média '+Math.round(quality*100)+'%).'+(micLatencyMs?' Latência de captura descontada: '+Math.round(micLatencyMs)+' ms.':' A latência interna do microfone não foi informada pelo Android; o resultado é uma estimativa de loopback.'));
 }catch(e){
  if(!run.cancelled)status((e&&e.message?e.message:'Falha na calibração.')+' O ajuste manual continua disponível.');
 }finally{
  calRelease(run);
  if(run.ctx&&run.ctx.state!=='closed')try{await run.ctx.close()}catch(_){}
  if(CAL_RUN===run)CAL_RUN=null;
  if(start){start.disabled=false;start.textContent='Calibrar novamente'}
  if(stopBtn)stopBtn.hidden=true;
  if(visual)visual.classList.remove('is-active');
 }
}
"""
start=h.index("const calHTML=()=>")
end=h.index("const CH={",start)
h=h[:start]+cal+h[end:]

# Expand the correction slider to cover the observed range of Bluetooth loopback delays.
h=h.replace("function setLat(v){v=Math.max(0,Math.min(300,+v||0));","function setLat(v){v=Math.max(0,Math.min(800,+v||0));",1)

# 3. Player visibility is independent from the step-2 body.pl layout class.
runtime=r"""
<script id="rimalab-player-visibility-runtime-v36">
(function(){
 'use strict';
 const body=document.body;
 const oldSet=window.zSetPL;
 if(typeof oldSet==='function'&&!oldSet.__rimaV36){
  const wrapped=function(v){
   const result=oldSet.apply(this,arguments);
   if(v)body.classList.add('rima-player-visible');
   return result;
  };
  wrapped.__rimaV36=true;window.zSetPL=wrapped;
 }
 const oldStop=window.stop;
 if(typeof oldStop==='function'&&!oldStop.__rimaV36){
  const wrapped=function(){
   body.classList.remove('rima-player-visible');
   return oldStop.apply(this,arguments);
  };
  wrapped.__rimaV36=true;window.stop=wrapped;
 }
 const oldNext=window.trainNext;
 if(typeof oldNext==='function'&&!oldNext.__rimaV36){
  const wrapped=function(){
   if(body.classList.contains('pv')&&typeof window.stop==='function')window.stop();
   body.classList.remove('rima-player-visible');
   return oldNext.apply(this,arguments);
  };
  wrapped.__rimaV36=true;window.trainNext=wrapped;
 }
 const oldBack=window.trainBack;
 if(typeof oldBack==='function'&&!oldBack.__rimaV36){
  const wrapped=function(){
   if(body.classList.contains('pv')&&typeof window.stop==='function')window.stop();
   body.classList.remove('rima-player-visible');
   return oldBack.apply(this,arguments);
  };
  wrapped.__rimaV36=true;window.trainBack=wrapped;
 }
 function restoreVisibility(){
  if(!body.classList.contains('pl'))body.classList.remove('rima-player-visible');
 }
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)restoreVisibility()});
 window.addEventListener('pageshow',restoreVisibility);
})();
</script>
"""
pos=h.lower().rfind('</body>')
h=h[:pos]+runtime+'\n'+h[pos:]

# 4. Mode heading, numbering and banner label.
modefix=r"""
<style id="rimalab-mode-number-clean-v37">
#rima-v29-mode-banner:before{display:none!important;content:none!important}
</style>
<script id="rimalab-mode-number-clean-runtime-v37">
(function(){
 function setText(el,value){if(el&&el.textContent!==value)el.textContent=value}
 function fix(){
  const step=document.getElementById('train-step-2');if(!step)return;
  const banner=document.getElementById('rima-v29-mode-banner');
  const head=step.querySelector('.stp');
  if(head){setText(head.querySelector('h2'),'Escolha o modo');setText(head.querySelector('.n'),'1')}
  if(banner){const title=banner.querySelector('strong');if(title){const next=title.textContent.replace(/^\\s*1\\s*[·.:-]\\s*/,'');setText(title,next)}}
  const df=document.getElementById('dfw');
  if(df){setText(df.querySelector('.stp h2'),'Dificuldade');setText(df.querySelector('.stp .n'),'2')}
  const bp=document.getElementById('bp');
  if(bp){const h=bp.previousElementSibling;if(h&&h.classList.contains('stp')){setText(h.querySelector('h2'),'Escolha o beat');setText(h.querySelector('.n'),'3')}}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fix,{once:true});else fix();
 const step=document.getElementById('train-step-2');
 if(step)new MutationObserver(()=>requestAnimationFrame(fix)).observe(step,{childList:true,subtree:true});
 document.addEventListener('click',e=>{if(e.target.closest('#rima-v29-mode-toggle,#rima-v29-mode-list [data-mode]'))setTimeout(fix,40)});
})();
</script>
"""
pos=h.lower().rfind('</body>')
h=h[:pos]+modefix+'\n'+h[pos:]

# 5. Refit the main word and rhyme suggestions every time viewport/orientation changes.
stage=r"""
<style id="rimalab-orientation-stage-fit-v36">
#lv:not([hidden]) #stg.stage{min-width:0!important;box-sizing:border-box!important;overflow:hidden!important}
#lv:not([hidden]) #stg.stage #cb{letter-spacing:.022em!important;line-height:1.08!important;white-space:nowrap!important;max-width:100%!important;box-sizing:border-box!important}
#lv:not([hidden]) #stg.stage #rm{position:relative!important;inset:auto!important;display:flex!important;flex-wrap:wrap!important;justify-content:center!important;align-items:center!important;gap:7px!important;margin:8px auto 10px!important;padding:0 5px!important;width:100%!important;min-height:0!important;height:auto!important}
#lv:not([hidden]) #stg.stage #rm>*{max-width:48%!important;min-width:0!important;white-space:nowrap!important;line-height:1.12!important;letter-spacing:.005em!important}
#lv:not([hidden]) #stg.stage .v3bar{margin-top:13px!important}
@media(orientation:landscape){
 #lv:not([hidden]){gap:10px 14px!important}
 #lv:not([hidden]) #stg.stage{min-height:0!important;height:calc(100svh - 110px)!important;max-height:calc(100svh - 110px)!important;padding:12px 14px!important}
 #lv:not([hidden]) #stg.stage #cb{margin:2px auto!important;padding:5px 3px!important}
 #lv:not([hidden]) #stg.stage #rm{margin:9px auto 11px!important;gap:8px!important}
 #lv:not([hidden]) #stg.stage #rm>*{padding:4px 8px!important}
 #lv:not([hidden]) #stg.stage .v3bar{margin-top:13px!important}
}
</style>
<script id="rimalab-orientation-stage-fit-runtime-v36">
(function(){
 'use strict';
 const $=s=>document.querySelector(s);
 let raf=0;
 function fitHints(){
  const word=$('#cb'),hints=$('#rm'),stage=$('#stg');
  if(!word||!hints||!stage||!stage.clientWidth)return;
  const main=parseFloat(getComputedStyle(word).fontSize)||56;
  const landscape=matchMedia('(orientation:landscape)').matches;
  const cap=landscape?16:18,ratio=landscape?.24:.26;
  const size=Math.max(12,Math.min(cap,main*ratio));
  hints.querySelectorAll(':scope > *').forEach(el=>{
   el.style.setProperty('font-size',size.toFixed(1)+'px','important');
   el.style.setProperty('line-height','1.12','important');
   el.style.setProperty('letter-spacing','.005em','important');
   el.style.setProperty('padding',landscape?'4px 8px':'5px 10px','important');
   el.style.setProperty('max-width','48%','important');
  });
 }
 function fitMain(){
  const word=$('#cb'),stage=$('#stg');if(!word||!stage||!stage.clientWidth)return;
  const text=(word.textContent||'').trim();if(!text)return;
  const range=document.createRange();try{range.selectNodeContents(word)}catch(_){return}
  const widthLimit=stage.clientWidth-34,landscape=matchMedia('(orientation:landscape)').matches;
  const heightLimit=Math.max(48,Math.min(stage.clientHeight*(landscape?.30:.34),landscape?118:170));
  let current=parseFloat(getComputedStyle(word).fontSize)||56;
  const measure=()=>{const r=range.getBoundingClientRect();return {w:r.width,h:r.height}};
  let box=measure();
  if(box.w>widthLimit||box.h>heightLimit){
   let lo=18,hi=current;
   for(let i=0;i<13;i++){const m=(lo+hi)/2;word.style.setProperty('font-size',m.toFixed(1)+'px','important');box=measure();if(box.w<=widthLimit&&box.h<=heightLimit)lo=m;else hi=m}
   word.style.setProperty('font-size',Math.max(18,lo).toFixed(1)+'px','important');
  }
 }
 function runFit(){cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{fitMain();fitHints()})}
 function settleOrientation(){requestAnimationFrame(()=>requestAnimationFrame(runFit))}
 function init(){
  const word=$('#cb'),stage=$('#stg'),hints=$('#rm');if(!word||!stage)return;
  new MutationObserver(runFit).observe(word,{childList:true,subtree:true,characterData:true});
  if(hints)new MutationObserver(fitHints).observe(hints,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(runFit).observe(stage);
  window.addEventListener('resize',settleOrientation,{passive:true});
  window.addEventListener('orientationchange',()=>setTimeout(settleOrientation,100),{passive:true});
  if(window.visualViewport)window.visualViewport.addEventListener('resize',settleOrientation,{passive:true});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)settleOrientation()});
  runFit();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
</script>
"""
pos=h.lower().rfind('</body>')
h=h[:pos]+stage+'\n'+h[pos:]

g=gp.read_text(encoding='utf-8')
m=re.search(r'\bversionCode\s+(\d+)',g)
if not m:raise SystemExit('V36_FAIL: versionCode ausente')
if int(m.group(1))<56:g=g[:m.start(1)]+'56'+g[m.end(1):]
m=re.search(r"""versionName\s+['"]([^'"]+)['"]""",g)
if not m:raise SystemExit('V36_FAIL: versionName ausente')
g=g[:m.start(1)]+'3.1.5'+g[m.end(1):]
# The previous v35 ticker reapplied 58px inline every 900ms; replace both CSS and JS literals.
h=h.replace('calc(58px + env(safe-area-inset-bottom,0px))','calc(4px + env(safe-area-inset-bottom,0px))')
h=h.replace('calc(58px + env(safe-area-inset-bottom, 0px))','calc(4px + env(safe-area-inset-bottom, 0px))')
hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V37_OK: player on-demand; hide on stop/exit; microphone loopback correlation over five chirps; automatic LAT estimate; mode numbering; orientation-responsive typography; landscape player bottom dock; version 3.1.4')
