#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve()
hp=root/'app/src/main/assets/rima-lab.html'
gp=root/'app/build.gradle'
h=hp.read_text(encoding='utf-8')

old_go="let tab=0;function go(i){LVFROM=0;if(i==0){if($('#train-step-1'))$('#train-step-1').hidden=false;if($('#train-step-2'))$('#train-step-2').hidden=true}if(i!=tab){if(play)stop();if(!$('#lv').hidden){addMin();$('#su').hidden=false;$('#lv').hidden=true}if(B)B.run=0;if(S)S.live=false;tab=i;if(i==2)bhome()}$$('.tab').forEach((e,j)=>e.hidden=j!=i);$$('nav button').forEach(b=>b.classList.toggle('on',+b.dataset.i==i))}"
new_go="""let tab=0;function go(i){LVFROM=0;const keepConfig=window.__rimaTrainStep===2&&$('#lv').hidden;window.__rimaKeepPlayerOnNavigation=keepConfig;if(i==0){const step2=window.__rimaTrainStep===2;if($('#train-step-1'))$('#train-step-1').hidden=step2;if($('#train-step-2'))$('#train-step-2').hidden=!step2}if(i!=tab){if(play&&!keepConfig)stop();if(!$('#lv').hidden){addMin();$('#su').hidden=false;$('#lv').hidden=true}if(B)B.run=0;if(S)S.live=false;tab=i;if(i==2)bhome()}$$('.tab').forEach((e,j)=>e.hidden=j!=i);$$('nav button').forEach(b=>b.classList.toggle('on',+b.dataset.i==i));window.__rimaKeepPlayerOnNavigation=false}"""
if old_go in h:h=h.replace(old_go,new_go,1)
elif 'const keepConfig=window.__rimaTrainStep===2' not in h:raise SystemExit('V28_FAIL: função go() não corresponde à versão esperada')

old_bhome='function bhome(){stop();if(B)B.run=0;'
new_bhome='function bhome(){if(!window.__rimaKeepPlayerOnNavigation)stop();if(B)B.run=0;'
if old_bhome in h:h=h.replace(old_bhome,new_bhome,1)
elif new_bhome not in h:raise SystemExit('V28_FAIL: bhome() não encontrado')

old_train="function trainNext(){if(!mode)mode='pal';$('#train-step-1').hidden=true;$('#train-step-2').hidden=false;window.scrollTo({top:0,behavior:'smooth'});try{zBarUI()}catch(e){}}\nfunction trainBack(){if($('#train-step-2'))$('#train-step-2').hidden=true;$('#train-step-1').hidden=false;window.scrollTo({top:0,behavior:'smooth'})}"
new_train="function trainNext(){if(!mode)mode='pal';$('#train-step-1').hidden=true;$('#train-step-2').hidden=false;window.__rimaTrainStep=2;document.body.classList.add('pl');window.scrollTo({top:0,behavior:'smooth'});try{zBarUI()}catch(e){}}\nfunction trainBack(){if($('#train-step-2'))$('#train-step-2').hidden=true;$('#train-step-1').hidden=false;window.__rimaTrainStep=1;if(!play)document.body.classList.remove('pl');window.scrollTo({top:0,behavior:'smooth'})}"
if old_train in h:h=h.replace(old_train,new_train,1)
elif 'window.__rimaTrainStep=2' not in h:raise SystemExit('V28_FAIL: trainNext()/trainBack() não encontrados')

persist=r"""<script id="rimalab-step2-persistence-v28">
(function(){
 const KEY='rimalab_training_config_v28';
 window.__rimaTrainStep=window.__rimaTrainStep||1;
 let restoring=true;
 const save=()=>{
  if(restoring)return;
  try{localStorage.setItem(KEY,JSON.stringify({v:1,step:window.__rimaTrainStep||1,mode:mode,nb4:nb4,fmt:fmt,CH:CH,DF:DF,LAT:LAT}))}catch(e){}
 };
 const oldMode=setMode;setMode=function(v){oldMode(v);save()};
 const oldChp=chp;chp=function(k,v){oldChp(k,v);save()};
 const oldN=setN;setN=function(v){oldN(v);save()};
 const oldDF=setDF;setDF=function(v){oldDF(v);save()};
 const oldLat=setLat;setLat=function(v){oldLat(v);save()};
 const oldNext=trainNext;trainNext=function(){oldNext();window.__rimaTrainStep=2;document.body.classList.add('pl');try{zBarUI()}catch(e){}save()};
 const oldBack=trainBack;trainBack=function(){oldBack();window.__rimaTrainStep=1;if(!play)document.body.classList.remove('pl');save()};
 try{
  const raw=localStorage.getItem(KEY),s=raw?JSON.parse(raw):null;
  if(s&&s.v===1){
   if(s.CH&&typeof s.CH==='object')Object.keys(CH).forEach(k=>{if(Object.prototype.hasOwnProperty.call(s.CH,k))CH[k]=s.CH[k]});
   if(Number.isFinite(+s.nb4))setN(+s.nb4);
   if(typeof s.mode==='string'&&MD3.some(x=>x[0]===s.mode))setMode(s.mode);
   if(typeof s.DF==='string'&&DIF[s.DF])setDF(s.DF);
   if(typeof s.fmt==='string')fmt=s.fmt;
   if(Number.isFinite(+s.LAT))setLat(+s.LAT);
   if(s.step===2){window.__rimaTrainStep=2;$('#train-step-1').hidden=true;$('#train-step-2').hidden=false;document.body.classList.add('pl');try{zBarUI()}catch(e){}}
  }
 }catch(e){}
 restoring=false;save();
})();
</script>"""
if 'id="rimalab-step2-persistence-v28"' not in h:
 pos=h.lower().rfind('</body>')
 if pos<0:raise SystemExit('V28_FAIL: body não encontrado para persistência')
 h=h[:pos]+persist+'\n'+h[pos:]

pattern=r"const calHTML=\(\)=>'[\s\S]*?';\nlet CAL_RUN=null;"
calhtml=r"""const calHTML=()=>'<section class="card calibrator-card"><div class="cal-top"><span class="cal-icon" aria-hidden="true">♫</span><div><h2>Sincronização Bluetooth</h2><p class="mut">Ajuste fino entre o áudio e o palco.</p></div></div><div class="cal-help"><p>Toque em testar: a caixa Bluetooth emitirá uma sequência de tons. Compare cada som com o sinal visual e ajuste a barra até os dois coincidirem.</p></div><div class="cal-visual" id="cal-visual" aria-live="off"><span></span><b>Referência visual</b></div><div class="cal-control"><div class="cal-value"><span class="lat-v">'+LAT+'</span><small>ms</small></div><input type="range" class="lat-s" min="0" max="300" step="1" value="'+LAT+'" oninput="setLat(+this.value)" aria-label="Ajuste da sincronização com caixa Bluetooth"></div><div class="cal-actions"><button id="cal-start" class="btn w cal-button" onclick="cal()">Testar sincronização</button><button id="cal-stop" class="btn g w cal-stop" onclick="calCancel()" hidden>Parar teste</button></div><p class="mut cm" role="status" aria-live="polite">Pronto para testar. O ajuste atual é de '+LAT+' ms.</p></section>';
let CAL_RUN=null;"""
h,n=re.subn(pattern,calhtml,h,count=1)
if n!=1:raise SystemExit('V28_FAIL: calHTML() não encontrado')

cancel=r"""function calCancel(){
 const r=CAL_RUN;if(!r)return;
 r.cancelled=true;
 if(r.timer)clearTimeout(r.timer);
 if(r.raf)cancelAnimationFrame(r.raf);
 for(const pair of r.sources){for(const node of pair){try{node.stop()}catch(_){}}}
 r.sources.clear();
 if(r.finish)r.finish();
 $$('.cm').forEach(e=>e.textContent='Teste interrompido. Nenhuma configuração foi alterada.');
 const a=$('#cal-start'),b=$('#cal-stop');
 if(a){a.disabled=false;a.textContent='Testar novamente'}if(b)b.hidden=true;
}"""
h,n=re.subn(r"function calCancel\(\){[\s\S]*?\}\nfunction setLat",cancel+"\nfunction setLat",h,count=1)
if n!=1:raise SystemExit('V28_FAIL: calCancel() não encontrado')

cal=r"""async function cal(){
 if(CAL_RUN)return;
 const run={cancelled:false,sources:new Set(),ctx:null,timer:null,raf:0,finish:null};CAL_RUN=run;
 const start=$('#cal-start'),stopBtn=$('#cal-stop'),visual=$('#cal-visual');
 const status=t=>$$('.cm').forEach(e=>e.textContent=t);
 if(start){start.disabled=true;start.textContent='Emitindo sinais...'}
 if(stopBtn)stopBtn.hidden=false;
 if(visual)visual.classList.remove('is-active');
 try{
  const AC=window.AudioContext||window.webkitAudioContext;
  if(!AC)throw new Error('AudioContext indisponível');
  const ctx=run.ctx=new AC({latencyHint:'interactive'});await ctx.resume();
  if(run.cancelled)return;
  status('A caixa Bluetooth está emitindo os tons. Compare o som com o brilho na tela e ajuste a barra.');
  const notes=[784,988,1175,988,784,1175],startAt=ctx.currentTime+.32;
  notes.forEach((hz,i)=>{
   const at=startAt+i*.72,osc=ctx.createOscillator(),harm=ctx.createOscillator(),main=ctx.createGain(),soft=ctx.createGain();
   osc.type='sine';osc.frequency.setValueAtTime(hz,at);
   harm.type='sine';harm.frequency.setValueAtTime(hz*2,at);
   main.gain.setValueAtTime(.0001,at);main.gain.exponentialRampToValueAtTime(.64,at+.014);main.gain.exponentialRampToValueAtTime(.0001,at+.22);
   soft.gain.setValueAtTime(.0001,at);soft.gain.exponentialRampToValueAtTime(.13,at+.014);soft.gain.exponentialRampToValueAtTime(.0001,at+.18);
   osc.connect(main);main.connect(ctx.destination);harm.connect(soft);soft.connect(ctx.destination);
   osc.start(at);harm.start(at);osc.stop(at+.24);harm.stop(at+.20);run.sources.add([osc,harm]);
   const delay=Math.max(0,(at-ctx.currentTime)*1000);
   setTimeout(()=>{if(!run.cancelled&&visual){visual.classList.add('is-active');setTimeout(()=>visual.classList.remove('is-active'),210)}},delay);
  });
  await new Promise(resolve=>{run.finish=resolve;run.timer=setTimeout(resolve,notes.length*720+900)});
  if(!run.cancelled)status('Teste concluído. Se o som chegar antes ou depois do brilho, ajuste a barra até coincidirem.');
 }catch(e){
  if(!run.cancelled)status('Não foi possível emitir os tons. Confira o volume e a conexão da caixa Bluetooth e tente novamente.');
 }finally{
  if(run.timer)clearTimeout(run.timer);
  for(const pair of run.sources){for(const node of pair){try{node.stop()}catch(_){}}}
  if(run.ctx)try{await run.ctx.close()}catch(e){}
  if(CAL_RUN===run)CAL_RUN=null;
  if(start){start.disabled=false;start.textContent='Testar sincronização'}
  if(stopBtn)stopBtn.hidden=true;
  if(visual)visual.classList.remove('is-active');
 }
}"""
h,n=re.subn(r"async function cal\(\){[\s\S]*?\n\}\nconst CH=",cal+"\nconst CH=",h,count=1)
if n!=1:raise SystemExit('V28_FAIL: cal() não encontrado')

css=r"""<style id="rimalab-calibration-polish-v28">
#vzb{margin-top:0!important;padding-top:0!important}
#vzb .calibrator-card{margin-top:8px!important;padding:12px 14px!important;gap:0!important}
.calibrator-card .cal-top{gap:10px!important;margin:0 0 8px!important}
.calibrator-card .cal-icon{width:38px!important;height:38px!important;flex-basis:38px!important;font-size:20px!important}
.calibrator-card .cal-help{padding:8px 10px!important;margin:0 0 8px!important;font-size:11.5px!important;line-height:1.42!important}
.calibrator-card .cal-help p{margin:0!important;color:#c4cbbd!important}
.calibrator-card .cal-visual{height:42px!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:9px!important;margin:0 0 8px!important;border:1px solid rgba(215,251,87,.14)!important;border-radius:11px!important;background:rgba(215,251,87,.025)!important;color:#9ca692!important;font-size:10px!important;letter-spacing:.04em!important;text-transform:uppercase!important}
.calibrator-card .cal-visual span{width:10px!important;height:10px!important;border-radius:50%!important;background:#66705e!important;box-shadow:0 0 0 4px rgba(215,251,87,.06)!important;transition:background .08s,box-shadow .08s,transform .08s!important}
.calibrator-card .cal-visual.is-active span{background:#e5ff87!important;transform:scale(1.35)!important;box-shadow:0 0 0 7px rgba(215,251,87,.12),0 0 18px rgba(215,251,87,.72)!important}
.calibrator-card .cal-control{padding:8px 10px!important;margin:0 0 8px!important;gap:10px!important}
.calibrator-card .cal-actions{gap:6px!important}
.calibrator-card .cal-button{min-height:42px!important}
.calibrator-card .cm{margin:7px 2px 0!important;min-height:12px!important;font-size:10.5px!important;line-height:1.4!important}
@media(max-width:360px){#vzb .calibrator-card{padding:11px!important}.calibrator-card .cal-help{padding:8px!important}}
</style>"""
if 'id="rimalab-calibration-polish-v28"' not in h:
 pos=h.lower().rfind('</body>')
 if pos<0:raise SystemExit('V28_FAIL: body não encontrado para CSS')
 h=h[:pos]+css+'\n'+h[pos:]

wordfit=r"""<script id="rimalab-word-fit-v28">
(function(){
 const fit=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');
  if(!e||!stage||!stage.clientWidth||!e.textContent.trim())return;
  const raw=e.textContent.trim(),len=Array.from(raw).length;
  const available=Math.max(100,stage.clientWidth-30);
  const maxHeight=Math.max(46,Math.min(stage.clientHeight*.48,210));
  const cap=len<=5?88:len<=8?80:len<=12?70:len<=16?62:54;
  const measure=()=>{try{const r=document.createRange();r.selectNodeContents(e);const b=r.getBoundingClientRect();return {w:b.width,h:b.height}}catch(_){return {w:e.scrollWidth,h:e.getBoundingClientRect().height}}};
  e.style.setProperty('display','block','important');e.style.setProperty('box-sizing','border-box','important');
  e.style.setProperty('width','100%','important');e.style.setProperty('max-width','100%','important');
  e.style.setProperty('padding','2px 2px 4px','important');e.style.setProperty('margin','0 auto','important');
  e.style.setProperty('white-space','nowrap','important');e.style.setProperty('word-break','normal','important');e.style.setProperty('overflow-wrap','normal','important');
  e.style.setProperty('line-height','1.06','important');e.style.setProperty('font-size',cap+'px','important');
  let b=measure();
  if(b.w>available||b.h>maxHeight){let low=40,high=cap;for(let i=0;i<14;i++){const mid=(low+high)/2;e.style.setProperty('font-size',mid.toFixed(1)+'px','important');b=measure();if(b.w<=available&&b.h<=maxHeight)low=mid;else high=mid}e.style.setProperty('font-size',Math.floor(low)+'px','important')}
 };
 const boot=()=>{
  const e=document.getElementById('cb'),stage=document.getElementById('stg');if(!e||!stage)return;
  new MutationObserver(()=>requestAnimationFrame(fit)).observe(e,{childList:true,subtree:true,characterData:true});
  if(typeof ResizeObserver!=='undefined')new ResizeObserver(()=>requestAnimationFrame(fit)).observe(stage);
  window.addEventListener('resize',fit,{passive:true});window.addEventListener('orientationchange',()=>setTimeout(fit,120),{passive:true});
  requestAnimationFrame(fit);
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
</script>"""
oldfit=r'<script id="(?:rima-word-fit-script-v13|rima-word-fit-script-v15|rimalab-word-fit-v17|rimalab-word-vertical-fit-script-v24|rimalab-word-fit-v26)">[\s\S]*?</script>'
h,n=re.subn(oldfit,'',h)
if n<5:raise SystemExit('V28_FAIL: não removi todos os cinco ajustadores antigos de tipografia')
if 'id="rimalab-word-fit-v26"' in h:raise SystemExit('V28_FAIL: ajustador v26 antigo ainda existe')
pos=h.lower().rfind('</body>')
h=h[:pos]+wordfit+'\n'+h[pos:]

g=gp.read_text(encoding='utf-8')
if re.search(r'\bversionCode\s+46\b',g):g=re.sub(r'\bversionCode\s+46\b','versionCode 47',g,count=1)
elif not re.search(r'\bversionCode\s+47\b',g):raise SystemExit('V28_FAIL: versionCode inesperado')
if "versionName '3.0.4'" in g:g=g.replace("versionName '3.0.4'","versionName '3.0.5'",1)
elif "versionName '3.0.5'" not in g:raise SystemExit('V28_FAIL: versionName inesperado')

hp.write_text(h,encoding='utf-8');gp.write_text(g,encoding='utf-8')
print('V28_OK: player persistente na etapa 2; configurações e calibração salvas; calibrador compacto com tons audíveis e referência visual; tipografia adaptativa maior; versão 3.0.5')
